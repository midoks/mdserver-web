<?php
// Executed once per request, front-controller style.
header('content-type: text/plain');
echo 'classic: ', $_SERVER['REQUEST_METHOD'], ' ', $_SERVER['REQUEST_URI'], "\n";