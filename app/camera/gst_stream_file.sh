gst-launch-1.0 -v filesrc location="$1" ! decodebin ! videoconvert \
    ! x264enc tune=zerolatency speed-preset=superfast \
    ! rtph264pay ! udpsink host=127.0.0.1 port=5000
