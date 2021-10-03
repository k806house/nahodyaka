gst-launch-1.0 -v autovideosrc device="/dev/video0" \
    ! video/x-raw,framerate=3/1 ! videoscale ! videoconvert \
    ! x264enc tune=zerolatency speed-preset=superfast \
    ! rtph264pay ! udpsink host=127.0.0.1 port=5000
