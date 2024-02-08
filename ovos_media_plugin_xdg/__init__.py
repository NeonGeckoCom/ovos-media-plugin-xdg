import signal
import subprocess
import time
from time import sleep

from ovos_plugin_manager.templates.media import AudioPlayerBackend, VideoPlayerBackend, MediaBackend
from ovos_utils.log import LOG


class XDGOpenMediaService(MediaBackend):

    def __init__(self, config, bus=None):
        super().__init__(config, bus)
        self.process = None
        self._stop_signal = False
        self._is_playing = False
        self._paused = False
        self.ts = 0

    def on_track_start(self):
        self.ts = time.time()
        # Indicate to audio service which track is being played
        if self._track_start_callback:
            self._track_start_callback(self._now_playing)

    def on_track_end(self):
        self._is_playing = False
        self._paused = False
        self.process = None
        self.ts = 0
        if self._track_start_callback:
            self._track_start_callback(None)

    def on_track_error(self):
        self._is_playing = False
        self._paused = False
        self.process = None
        self.ts = 0
        self.ocp_error()

    # xdg player internals
    def _is_process_running(self):
        return self.process and self.process.poll() is None

    def _stop_running_process(self):
        if self._is_process_running():
            if self._paused:
                # The child process must be "unpaused" in order to be stopped
                self.process.send_signal(signal.SIGCONT)
            self.process.terminate()
            countdown = 10
            while self._is_process_running() and countdown > 0:
                sleep(0.1)
                countdown -= 1

            if self._is_process_running():
                # Failed to shutdown when asked nicely.  Force the issue.
                LOG.debug("Killing currently playing audio...")
                self.process.kill()
        self.process = None

    # audio service
    def supported_uris(self):
        # get mime -  xdg-mime query filetype example.png
        return ['file', 'http', 'https', 'ftp']

    def play(self, repeat=False):
        """ Play playlist using xdg. """
        # Stop any existing audio playback
        self._stop_running_process()

        self._is_playing = True
        self._paused = False

        # Replace file:// uri's with normal paths
        uri = self._now_playing.replace('file://', '')

        self.on_track_start()
        try:
            self.process = subprocess.Popen(["xdg-open", uri])
        except FileNotFoundError as e:
            LOG.error(f'Couldn\'t play audio, {e}')
            self.process = None
            self.on_track_error()
        except Exception as e:
            LOG.exception(repr(e))
            self.process = None
            self.on_track_error()

        # Wait for completion or stop request
        while (self._is_process_running() and not self._stop_signal):
            sleep(0.25)

        if self._stop_signal:
            self._stop_running_process()

        self.on_track_end()

    def stop(self):
        """ Stop xdg playback. """
        if self._is_playing:
            self._stop_signal = True
            while self._is_playing:
                sleep(0.1)
            self._stop_signal = False
            return True
        return False

    def pause(self):
        """ Pause xdg playback. """
        if self.process and not self._paused:
            # Suspend the playback process
            self.process.send_signal(signal.SIGSTOP)
            self._paused = True

    def resume(self):
        """ Resume paused playback. """
        if self.process and self._paused:
            # Resume the playback process
            self.process.send_signal(signal.SIGCONT)
            self._paused = False

    def lower_volume(self):
        """Lower volume.

        This method is used to implement audio ducking. It will be called when
        OpenVoiceOS is listening or speaking to make sure the media playing isn't
        interfering.
        """
        # Not available in this plugin

    def restore_volume(self):
        """Restore normal volume.

        Called when to restore the playback volume to previous level after
        OpenVoiceOS has lowered it using lower_volume().
        """
        # Not available in this plugin

    def get_track_length(self) -> int:
        """
        getting the duration of the audio in milliseconds
        """
        # we only can estimate how much we already played as a minimum value
        return self.get_track_position()

    def get_track_position(self) -> int:
        """
        get current position in milliseconds
        """
        # approximate given timestamp of playback start
        if self.ts:
            return int((time.time() - self.ts) * 1000)
        return 0

    def set_track_position(self, milliseconds):
        """
        go to position in milliseconds
          Args:
                milliseconds (int): number of milliseconds of final position
        """
        # Not available in this plugin


class XDGOpenAudioService(AudioPlayerBackend, XDGOpenMediaService):
    def __init__(self, config, bus=None):
        super().__init__(config, bus)


class XDGOpenVideoService(VideoPlayerBackend, XDGOpenMediaService):
    def __init__(self, config, bus=None):
        super().__init__(config, bus)
