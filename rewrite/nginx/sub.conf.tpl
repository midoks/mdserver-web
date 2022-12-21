location / {
    set $replace 'tmplate_replace';
    set $spider_request '0';

    if ($http_user_agent ~* '(baiduspider|360sipder|Sogou Orion spider|Sogou News Spider|Sogou blog|Sogou spider2|Sogou inst spider|Sogou web spider|Sogou spider|trendiction|Yahoo|semrush|Toutiao|Google|qihoobot|Googlebot|Googlebot-Mobile|Googlebot-Image|Mediapartners-Google|Adsbot-Google|Feedfetcher-Google|Yahoo! Slurp|Yahoo! Slurp China|YoudaoBot|Sosospider|MSNBot|ia_archiver|Tomato Bot)') {
        set $spider_request '1';
    }

    if ($spider_request = '0' ) {
        set $replace 'tmplate_replace';
    }

    sub_filter 'tmplate_replace' $replace;
    sub_filter_once on;
    sub_filter_types *;
}