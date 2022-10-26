#! /usr/bin/perl

# (C) 2001-2013 Aristotle Pagaltzis
# derived from code (C) 2001-2002 Frank Denis and Matthias Andree

use strict;

my ($conffile, @flg) = @ARGV;

my $PUREFTPD;
-x && ($PUREFTPD=$_, last) for qw(
        {$SERVER_PATH}/pureftp/sbin/pure-ftpd
        /www/server/pureftp/sbin/pure-ftpd
        /www/server/pureftpd/sbin/pure-ftpd
        /www/server/sbin/pure-ftpd
        /usr/sbin/pure-ftpd
);

my %simple_switch_for = (
        IPV4Only                        => "-4",
        IPV6Only                        => "-6",
        ChrootEveryone                  => "-A",
        BrokenClientsCompatibility      => "-b",
        Daemonize                       => "-B",
        VerboseLog                      => "-d",
        DisplayDotFiles                 => "-D",
        AnonymousOnly                   => "-e",
        NoAnonymous                     => "-E",
        DontResolve                     => "-H",
        AnonymousCanCreateDirs          => "-M",
        NATmode                         => "-N",
        CallUploadScript                => "-o",
        AntiWarez                       => "-s",
        AllowUserFXP                    => "-w",
        AllowAnonymousFXP               => "-W",
        ProhibitDotFilesWrite           => "-x",
        ProhibitDotFilesRead            => "-X",
        AllowDotFiles                   => "-z",
        AutoRename                      => "-r",
        AnonymousCantUpload             => "-i",
        LogPID                          => "-1",
        NoChmod                         => "-R",
        KeepAllFiles                    => "-K",
        CreateHomeDir                   => "-j",
        NoRename                        => "-G",
        CustomerProof                   => "-Z",
        NoTruncate                      => "-0",
);

my %string_switch_for = (
        FileSystemCharset       => "-8",
        ClientCharset           => "-9",
        SyslogFacility          => "-f",
        FortunesFile            => "-F",
        ForcePassiveIP          => "-P",
        Bind                    => "-S",
        AnonymousBandwidth      => "-t",
        UserBandwidth           => "-T",
        TrustedIP               => "-V",
        AltLog                  => "-O",
        PIDFile                 => "-g",
        TLSCipherSuite          => "-J",
        CertFile                => "-2",
);

my %numeric_switch_for = (
        MaxIdleTime             => "-I",
        MaxDiskUsage            => "-k",
        TrustedGID              => "-a",
        MaxClientsNumber        => "-c",
        MaxClientsPerIP         => "-C",
        MaxLoad                 => "-m",
        MinUID                  => "-u",
        TLS                     => "-Y",
);

my %numpairb_switch_for = (
        LimitRecursion          => "-L",
        PassivePortRange        => "-p",
        AnonymousRatio          => "-q",
        UserRatio               => "-Q",
);

my %numpairc_switch_for = (
        Umask           => "-U",
        Quota           => "-n",
        PerUserLimits   => "-y",
);

my %auth_method_for = (
        LDAPConfigFile          => "ldap",
        MySQLConfigFile         => "mysql",
        PGSQLConfigFile         => "pgsql",
        PureDB                  => "puredb",
        ExtAuth                 => "extauth",
);

my $simple_switch = qr/(@{[join "|", keys %simple_switch_for ]})\s+yes/i;
my $string_switch = qr/(@{[join "|", keys %string_switch_for ]})\s+(\S+)/i;
my $numeric_switch = qr/(@{[join "|", keys %numeric_switch_for ]})\s+(\d+)/i;
my $numpairb_switch = qr/(@{[join "|", keys %numpairb_switch_for ]})\s+(\d+)\s+(\d+)/i;
my $numpairc_switch = qr/(@{[join "|", keys %numpairc_switch_for ]})\s+(\d+):(\d+)/i;
my $auth_method = qr/(@{[join "|", keys %auth_method_for ]})\s+(\S+)/i;

die "Usage: pure-config.pl <configuration file> [extra options]\n"
        unless defined $conffile;

open CONF, "< $conffile" or die "Can't open $conffile: $!\n";

!/^\s*(?:$|#)/ and (chomp, push @flg,
        /$simple_switch/i               ? ($simple_switch_for{$1}) :
        /$string_switch/i               ? ($string_switch_for{$1} . $2) :
        /$numeric_switch/i              ? ($numeric_switch_for{$1} . $2) :
        /$numpairb_switch/i             ? ($numpairb_switch_for{$1} . "$2:$3") :
        /$numpairc_switch/i             ? ($numpairc_switch_for{$1} . "$2:$3") :
        /$auth_method/i                 ? ("-l" . "$auth_method_for{$1}:$2") :
        /UnixAuthentication\s+yes/i     ? ("-l" . "unix") :
        /PAMAuthentication\s+yes/i      ? ("-l" . "pam") :
        ()
) while <CONF>;

close CONF;

if (-t STDOUT) {
        print "Running: $PUREFTPD ", join(" ", @flg), "\n";
}
exec { $PUREFTPD } ($PUREFTPD, @flg) or die "cannot exec $PUREFTPD: $!";

