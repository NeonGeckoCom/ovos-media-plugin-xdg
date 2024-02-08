# ovos-media-plugin-xdg

plugin for [ovos-media](https://github.com/OpenVoiceOS/ovos-media)

[xdg-open](https://man.archlinux.org/man/xdg-open.1) opens a file or URL in the user's preferred application. 

If a URL is provided the URL will be opened in the user's preferred web browser.
If a file is provided the file will be opened in the preferred application for files of that type. 
xdg-open supports file, ftp, http and https URLs.

xdg-open is for use inside a desktop session only. It is not recommended to use xdg-open as root.

## Install

`pip install ovos-media-plugin-xdg`

## Configuration


```javascript
{
 "media": {

    // keys are the strings defined in "audio_players"
    "preferred_audio_services": ["mplayer", "vlc", "xdg"],

    // PlaybackType.AUDIO handlers
    "audio_players": {
        // xdg-open to handle uris
        "xdg": {
            // the plugin name
            "module": "ovos-media-audio-plugin-xdg",

            // users may request specific handlers in the utterance
            // using these aliases
            "aliases": ["System", "Desktop", "OS", "XDG Open"],

            // deactivate a plugin by setting to false
            "active": true
        }
    }
    
    "video_players": {
        // xdg-open to handle uris
        "xdg": {
            // the plugin name
            "module": "ovos-media-video-plugin-xdg",

            // users may request specific handlers in the utterance
            // using these aliases
            "aliases": ["System", "Desktop", "OS", "XDG Open"],

            // deactivate a plugin by setting to false
            "active": true
        }
    }
}
```