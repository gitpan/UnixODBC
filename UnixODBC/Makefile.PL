use ExtUtils::MakeMaker;
# See lib/ExtUtils/MakeMaker.pm for details of how to influence
# the contents of the Makefile that is written.

WriteMakefile(
    'NAME'		=> 'UnixODBC::BridgeServer',
    'VERSION_FROM'      => 'BridgeServer.pm',
    'PREREQ_PM'		=> {'RPC::PlServer' => undef,
			    'Net::Daemon' => undef,
			    'Storable' => undef,
			    'Sys::Syslog' => undef}, 
);
