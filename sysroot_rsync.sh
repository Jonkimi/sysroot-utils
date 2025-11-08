# !/bin/bash

rsync --info=progress2  -vaHAX --exclude={"/dev/*","/proc/*","/sys/*","/tmp/*","/run/*","/var/*","/home/*","/root/*","/boot/*","/opt/*","/swapfile","/mnt/*","/media/*","/lost+found"} source-root:/ dest-sysroot