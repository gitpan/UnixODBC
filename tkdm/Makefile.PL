use ExtUtils::MakeMaker;
# See lib/ExtUtils/MakeMaker.pm for details of how to influence
# the contents of the Makefile that is written.

my $packageversion = '0.16';

print "Tkdm, package version $packageversion\n";
print "Type \"man tkdm\" for instructions.\n";

WriteMakefile(
    'NAME'		=> 'tkdm',
    'VERSION'           => $packageversion,
    'EXE_FILES'         => ['tkdm'],
    'PREREQ_PM'		=> {'Tk' => undef,
			    'UnixODBC' => undef}, 
);



