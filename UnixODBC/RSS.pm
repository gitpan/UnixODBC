package UnixODBC::RSS;

# $Id: RSS.pm,v 1.6 2004/03/06 22:34:00 kiesling Exp $

our $VERSION=0.01;

@ISA = qw(Exporter);

use UnixODBC;

my $preamble = qq{<?xml version="1.0"?>
<!-- RSS Generated by UnixODBC::RSS.pm $VERSION

  UnixODBC::RSS is part of UnixODBC:
    <http://sourceforge.net/projects/unixodbc-pm>

    Refer to UnixODBC::RSS(3) for information.

--!>
};

sub new {
    my $proto = shift;
    my $self = { @_ };
    bless($self, (ref($proto) || $proto));
    $self;
}

sub Channel {
    my $self = shift;
    my $c = $_[0];
    $self -> {channel} = $c;
}

sub ItemColumns {
    my $self = shift;
    my $i = $_[0];
    $self -> {itemcolumns} = $i;
}

sub Output {
    my $self = shift;
    my $resultref = $_[0];
    my $fh = $_[1];
    my ($rows, $cols, $rref, $cidx);
    use UnixODBC::RSS::Ver10;
    push @ISA, (UnixODBC::RSS::Ver10);

    print $fh $preamble;
    print $fh $self -> rssopen . "\n";
    my $c = $self -> channeltagsref;
    my $i = $self -> itemtagsref;

    print $fh "  " . $c -> {open} . "\n";

    my $colheadref = shift @$resultref;

    foreach my $t (qw/title description link/) {
	print $fh "    " . 
	    $c->{"${t}open"}.$self->{channel}{$t}.$c -> {"${t}close"}."\n";
    }

    foreach $rref (@{$resultref}) {
	printf $fh "      " . $i -> {open} . "\n";
	for ($cidx = 0; $cidx <= $#{$rref}; $cidx++) {
	    foreach my $ic (keys %{$self -> {itemcolumns}} ) {
		if ($$colheadref[$cidx] eq $ic) {
		    local $s = $self -> {itemcolumns}{$ic};
		    print $fh "        ". $i -> {"${s}open"} . 
                      ${$rref}[$cidx] . 
                      $i -> {"${s}close"} . "\n";
		}
	    }
        }
	printf $fh "      " . $i -> {close} . "\n";
    } # foreach

    print "  ". $c -> {close} . "\n";

    print $self -> rssclose . "\n";

}



=head1 NAME

UnixODBC::RSS.pm - Create RSS output from a UnixODBC query.

=head1 SYNOPSIS

    use UnixODBC;
    use UnixODBC::RSS;

    my $rdf = new UnixODBC::RSS;  

    $rdf -> Channel ({'title' => 'feed_title',
		      'description' => 'feed_description',
		      'link' => 'url'});
		     

    $rdf -> ItemColumns ({'column_name_of_title_content' => 'title',
			 'column_name_of_description_content' => 'description',
			 'column_name_of_name_content' => 'name',
			 'column_name_of_link_content' => 'link'});

    $rdf -> Output (\@resultset, *STDOUT);  

=head1 DESCRIPTION

UnixODBC::RSS.pm formats query results as a RSS version 1.0 RDF file.
The result set must be an array of array references, with the first
row containing column names.

The Channel() method's argument is an anonymous hash or hash reference
that provides RSS channel identification for <channel> and member tags:
<title>, <description>, and <url>.

The method, ItemColumns(), takes as its argument an anonymous hash or
hash reference. Each key-value pair describes the result set column
that provides content for an <item> member: <title>, <name>,
<description>, or <link>.

Output() takes as its arguments the result set as an array reference and
an output filehandle.

Creating a RSS RDF file follows approximately these steps:


  # Allocate Environment, Connection, and statement handles, and connect 
  # to DSN.... 

  $r = SQLPrepare ($sth, $Query, length ($Query));
  $r = SQLExecute ($sth);

  my $ncols;

  $r = SQLNumResultCols ($sth,$ncols);

  my ($col, $buf, $rfetch, $rget, $colarrayref, @rowarray, $rlen, $n);

  my $colheadref = new_array_ref ();

  # Get column headings

  for ($col = 1; $col <= $ncols; $col++) {
      $r = SQLColAttribute ($sth, $col, $SQL_COLUMN_NAME, $buf, 
	  		  $SQL_MAX_MESSAGE_LENGTH, $rlen, $n);
      $$colheadref[$col - 1] = $buf;
  }

  push @rowarray, ($colheadref);

  # Get column data

  while (1) {
      $rfetch = SQLFetch ($sth);
      last if $rfetch == $SQL_NO_DATA;
      $colarrayref = new_array_ref ();
      for ( $col = 1; $col <= $ncols; $col++) {
	  $rget = SQLGetData ($sth, $col, $SQL_CHAR, $buf, 
		  	 $SQL_MAX_MESSAGE_LENGTH, $rlen);
          $$colarrayref[$col - 1] = $buf;
      }
      push @rowarray, ($colarrayref);
  }

  $rss -> Output (\@rowarray, *STDOUT);

  sub new_array_ref { my @a; return \@a; }


=head1 VERSION INFORMATION AND CREDITS

Version 0.01

Copyright � 2004 Robert Kiesling, rkies@cpan.org.

Licensed under the same terms as Perl.  Refer to the file, "Artistic,"
for details.

=head1 BUGS

This version does not perform validation and does not check for
required keys.  The <image> tag does not yet have an output method.

=head1 SEE ALSO

UnixODBC(3), XML::RSS(3), rssoutput(1)

=cut


1;
