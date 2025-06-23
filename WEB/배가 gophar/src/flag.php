<?php

if($_SERVER['REMOTE_ADDR'] == '127.0.0.1' && $_SERVER['HTTP_ADMIN_KEY'] == 's2cr3t'){
    echo "KCTF_Jr{c31c79e4635efba7ce230bd7403cbf9d}";
}else{
    die("no hack.");
}

?>