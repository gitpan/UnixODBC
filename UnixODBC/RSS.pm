package UnixODBC::RSS;

# $Id: RSS.pm,v 1.19 2004/03/23 19:40:08 kiesling Exp $

our $VERSION=0.02;

our @ISA = qw(Exporter);

use UnixODBC;

my $preamble = qq{<?xml version="1.0"?>
<!-- RDF 1.0 generated by UnixODBC::RSS, version $VERSION.

  UnixODBC::RSS is part of UnixODBC.pm: http://unixodbc-pm.sourceforge.net/.

  Refer to UnixODBC::RSS(3) for information.

-->
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

sub ChannelImage {
    my $self = shift;
    my $c = $_[0];
    $self -> {channelimage} = $c;
}

sub ItemColumns {
    my $self = shift;
    my $i = $_[0];
    $self -> {itemcolumns} = $i;
}

sub TextInput {
    my $self = shift;
    $self -> {textinput} = $_[0];
}

sub ColumnHeadings {
    my $self = shift;
    $self -> {columnheadings} = $_[0];
}

sub Output {
    my $self = shift;
    my $resultref = $_[0];
    my $fh = $_[1];
    use UnixODBC::RSS::Ver10;
    push @ISA, (UnixODBC::RSS::Ver10);

    print $fh $preamble .
	$self -> rssopen . "\n" .
	$self -> channel_as_str ($resultref) ; 
    print $fh $self -> image_as_str if ($self -> {channelimage});
    print $fh $self -> items_as_str ($resultref);
    print $fh $self -> textinput_as_str () if ($self -> {textinput});
    print $fh $self -> rssclose . "\n";

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
		     
    $rdf -> ChannelImage ('url' => 'image_url',
			  'title' => 'alt_title',
			  'description' => 'image_description');

    $rdf -> TextInput ({'title' => 'resource_title',
			'description' => 'resource_description',
			'name' => 'resource_name',
			'link' => 'resource_uri'});

    $rdf -> ColumnHeadings ($array_ref);

    $rdf -> ItemColumns ({'column_name_of_title_content' => 'title',
			 'column_name_of_description_content' => 'description',
			 'column_name_of_name_content' => 'name',
			 'column_name_of_link_content' => 'link'});

    # @resultset is an array of row references.
    $rdf -> Output (\@resultset, *STDOUT);  

=head1 DESCRIPTION

UnixODBC::RSS.pm formats query results as a RSS version 1.0 RDF file.
The result set array that is the Output () method's first argument is
an array of row array references, as described below.

The Channel() method's argument is an anonymous hash or hash reference
that provides RSS channel identification for <channel> and member tags:
<title>, <description>, and <url>.  

ChannelImage() optionally provides information about an image
resource, if any.  An <image><link> member content is identical to the
<channel><link> member content.

The method, ItemColumns(), takes as its argument an anonymous hash or
hash reference. Each key-value pair describes the result set column
that provides content for an <item> member: <title>, <name>,
<description>, or <link>.

ColumnHeadings() saves a query's column headings as an array reference.
Refer to the example below.

The TextInput() arguments, given as a hash reference, provide the
content of a <textinput> section.

Output() takes as its arguments the result set as an array reference and
an output filehandle.

Creating a RSS RDF file follows approximately these steps.


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

  $rss -> ColumnHeadings ($colheadref);

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

Version 0.02

Copyright � 2004 Robert Kiesling, rkies@cpan.org.

Licensed under the same terms as Perl.  Refer to the file, "Artistic,"
for details.

=head1 BUGS

Does not perform validation and does not check for required content.

=head1 SEE ALSO

UnixODBC(3), XML::RSS(3), rssoutput(1)

=cut


1;
