i=150; sudo convert front.jpeg \
      -compress jpeg \
      -quality 90 \
      -density ${i}x${i} \
      -units PixelsPerInch \
      -resize $((i*827/100))x$((i*1169/100)) \
      -repage $((i*827/100))x$((i*1169/100)) \
      -gravity center \
      front.pdf

