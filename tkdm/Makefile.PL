use ExtUtils::MakeMaker;
# See lib/ExtUtils/MakeMaker.pm for details of how to influence
# the contents of the Makefile that is written.

WriteMakefile(
    'NAME'		=> 'tkdm',
    'VERSION_FROM'      => 'tkdm',
    'EXE_FILES'         => ['tkdm'],
    'PREREQ_PM'		=> {'Tk' => undef,
			    'UnixODBC' => undef}, 
);



