package UnixODBC::Properties;

# $Id: RSS.pm,v 1.18 2004/03/13 23:03:42 kiesling Exp $

our $VERSION=0.02;

@ISA = qw(Exporter);

@EXPORT_OK =qw(&new);

=head1

    my $prop = name => undef,  # scalar
		 value => undef, # scalar
		 type => undef,  # int
		 data => undef,  # arrayref
		 help => undef   # scalar
		 

=head1

sub new {
    my $proto = shift;
    my $self = { @_ };
    bless($self, (ref($proto) || $proto));
    $self;
}

