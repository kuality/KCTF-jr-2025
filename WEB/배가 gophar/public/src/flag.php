<?php

if($_SERVER['REMOTE_ADDR'] == '127.0.0.1' && $_SERVER['HTTP_ADMIN_KEY'] == 's2cr3t'){
    echo "KCTF_Jr{this_is_fake}";
}else{
    die("no hack.");
}

?>