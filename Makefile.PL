use ExtUtils::MakeMaker;
# See lib/ExtUtils/MakeMaker.pm for details of how to influence
# the contents of the Makefile that is written.

my $packageversion = '0.16';

print "Writing Makefile for UnixODBC Version $packageversion:\n";

WriteMakefile(
    'NAME'		=> 'UnixODBC::BridgeServer',
    'VERSION'           => $packageversion,
    'PREREQ_PM'		=> {'RPC::PlServer' => 0,
			    'Net::Daemon' => 0,
			    'Storable' => 0,
			    'Sys::Syslog' => 0}, 
);

WriteMakefile(
    'NAME'		=> 'UnixODBC',
    'VERSION'           => $packageversion,
    'LIBS'		=> ['-lodbc'],
);



