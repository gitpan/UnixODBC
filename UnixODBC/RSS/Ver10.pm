package UnixODBC::RSS::Ver10;

# $Id: Ver10.pm,v 1.2 2004/03/06 22:07:29 kiesling Exp $

my $VERSION=0.01;

my %rsstags = ('open' => '<rss version ="1.0">',
	       'close' => '</rss>');

sub rssopen { return $rsstags{'open'}; }

sub rssclose { return $rsstags{'close'}; }

my $channeltags = {open => '<channel>',
		   close => '</channel>',
		   titleopen => '<title>',
		   titleclose => '</title>',
		   descriptionopen => '<description>',
		   descriptionclose => '</description>',
		   linkopen => '<link>',
		   linkclose => '</link>'};

sub channeltagsref {return $channeltags;}

my $imagetags = {open => '<image>',
	       close => '</image>',
	       titleopen => '<title>',
	       titleclose => '</title>',
	       urlopen => '<url>',
	       urlclose => '</url>',
	       linkopen => '<link>',
	       linkclose => '</link>'};

sub imagetagsref { return $imagetags; }

my $itemtags = {open => '<item>',
		close => '</item>',
		titleopen => '<title>',
		titleclose => '</title>',
		nameopen => '<name>',
		nameclose => '</name>',
		descriptionopen => '<description>',
		descriptionclose => '</description>',
		linkopen => '<link>',
		linkclose => '</link>'};

sub itemtagsref { return $itemtags; }
1;
