<?php
$cfg['blowfish_secret'] = '{$BLOWFISH_SECRET}';
$i                      = 0;
$i++;
$cfg['Servers'][$i]['verbose']   = '{$CHOOSE_DB}';
$cfg['Servers'][$i]['auth_type'] = 'cookie';
// $cfg['Servers'][$i]['host']            = '127.0.0.1';
// $cfg['Servers'][$i]['connect_type']    = 'tcp';
$cfg['Servers'][$i]['socket']          = '{$SERVER_PATH}/{$CHOOSE_DB_DIR}/mysql.sock';
$cfg['Servers'][$i]['connect_type']    = 'socket';
$cfg['Servers'][$i]['compress']        = false;
$cfg['Servers'][$i]['AllowNoPassword'] = false;
$cfg['TempDir']                        = '{$SERVER_PATH}/phpmyadmin/{$PMA_PATH}/tmp';
$cfg['UploadDir']                      = '';
$cfg['SaveDir']                        = '';
?>
