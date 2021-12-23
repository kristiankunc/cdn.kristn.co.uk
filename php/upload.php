<?php
    $disallowed = array("php", "js", "html", "php5", "php3", "php4", "phtml", "py", "pyc", "jsp", "sh", "cgi");
    header("Content-Type: text/text");
    $key = "uploadss.com";
    $uploadhost = "cnd.kristn.tech";
    $redirect = "cnd.kristn.tech";
    if (isset($_POST['k'])) {
        if ($_POST['k'] == $key) {
            $target = getcwd() . "/" . basename($_FILES['d']['name']);
            if (move_uploaded_file($_FILES['d']['tmp_name'], $target)) {
                $md5 = rand(0, 99999);
                $explode = explode(".", $_FILES["d"]["name"]);
                $extension = end($explode);
                if (in_array($extension, $disallowed)) {
                    unlink($target);
                    die();
                }
                rename(getcwd() . "/" . basename($_FILES['d']['name']), getcwd() . "/" . $md5 . "." . $extension);
                echo $uploadhost . $md5 . "." . $extension;
            } else {
                echo "Couldn't upload";
            }
        } else {
                    header('Location: '.$redirect);

        }
    } else {
                header('Location: '.$redirect);

    }
?>