#!/usr/local/bin/perl

use CGI;
use CGI::Carp qw(fatalsToBrowser);
use UnixODBC (':all');
use UnixODBC::BridgeServer;
use RPC::PlClient;

my $loginfile = '/usr/local/etc/odbclogins'; # File that contains login data.
my %peers; # Peer host login data from /usr/local/etc/odbclogins
&readlogins;

my $q = new CGI;

my $dsnquery = $ENV{'QUERY_STRING_UNESCAPED'};

my $peerport = 9999;
my $querytext;

my ($host, $dsn, $table, $user, $password, $querytext, @fields);

my $styleheader = <<END_OF_HEADER;
<!DOCTYPE html
	PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
	 "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" lang="en-US">
<head><title>Untitled Document</title>
<style type="text/css">
A {color: blue}
TEXTAREA {background-color: transparent}
DIV.dsnlist {margin-left: 2}
DIV.tablelist {margin-left: 4}
DIV.loginmsg {margin-left: 10}
</style>
</head>
END_OF_HEADER

# Print HTML header
&starthtml;

# Here's the state detemination thing.
if ($dsnquery =~ /hostdsntable/) { # From the dsn frame.
    ($host, $dsn, $table) = 
	($dsnquery =~ /hostdsntable=(.*?)--(.*?)--(.*?)\\&/);
    ($user, $password) = 
	($dsnquery =~ /username=(.*)\\&password=(.*)/);
    $dsn =~ s/\+/ /g;
    @fields = get_fields ($user, $password, $host, $dsn, $table);
} else { # When redrawing the query form
    $user = $q -> param ('username');
    $password = $q -> param ('password');
    $host = $q -> param ('host');
    $dsn = $q -> param ('dsn');
    $table = $q -> param ('table');
    @fields = get_fields ($user, $password, $host, $dsn, $table);
    $querytext = $q -> param ('querytext');
}

my $loginform = <<ENDOFLOGINFORM;
 <table align="center" cellpadding="0">
  <colgroup cols="5">
     <tr>
       <td><label>Data Source:</label></td>
       <td><label>Table:</label></td>
       <td><label>Host Name:</label></td>
       <td><label>User Name:</label></td>
       <td><label>Password:</label></td>
     </tr>
     <tr>
       <td><input type="text" name="dsn" value="$dsn"></td>
       <td><input type="text" name="table" value="$table"></td>
       <td><input type="text" name="host" value="$host"></td>
       <td><input type="text" name="username" value="$user"></td>
       <td><input type="password" name="password" value="$password"></td>
     </tr>
  </colgroup>
</table>
<p>
ENDOFLOGINFORM

my $sqltextform = <<ENDOFSQLTEXTFORM;
 <form action="/cgi-bin/tables.cgi">
 <table align="center" cellpadding="0">
  <colgroup cols="5">
     <tr>
       <td><label>Data Source:</label></td>
       <td><label>Table:</label></td>
       <td><label>Host Name:</label></td>
       <td><label>User Name:</label></td>
       <td><label>Password:</label></td>
     </tr>
     <tr>
       <td><input type="text" name="dsn" value="$dsn"></td>
       <td><input type="text" name="table" value="$table"></td>
       <td><input type="text" name="host" value="$host"></td>
       <td><input type="text" name="username" value="$user"></td>
       <td><input type="password" name="password" value="$password"></td>
     </tr>
     <tr>
       <td colspan="5">
         <label>SQL Query Text:</label><br>
         <textarea cols="80" rows="5" name="querytext">$querytext</textarea>
       </td>
     </tr>
     <tr>
       <td colspan="5">
         <input type="submit" name="gettextbox" value="Text Query">
         <input type="submit" name="submitquery" value="SELECT Query">
       </td>
     </tr>
  </colgroup>
</table>
</form>
<hr>
ENDOFSQLTEXTFORM

# Here's the state determination thing again,
# because the forms needed to be parsed.
if ($q -> param ('gettextbox') =~ /Text Query/) { # From text box form
    print $sqltextform;
    $querytext = $q -> param ('querytext');
    &doclientquery if (defined $querytext and length ($querytext));
} elsif ($q -> param ('submitquery') =~ /Submit Query/) { # From select form
    &fieldform (@fields);
    $querytext = &buildquery;
    &doclientquery;
} elsif ($q->param ('submitquery') =~ /SELECT Query/){#Return to SELECT form
    &fieldform (@fields);
} else { # From anywhere else
    &fieldform (@fields);
}

&endhtml;

### 
### Subroutines 
###

sub buildquery {
    my @params = $q -> param;
    my ($localparam, $querystring, @selectedfields, %predicates);
    my ($tmppred, $npreds);
    $npreds = 0;
    foreach my $p (@params) {
	$localparam = $q -> param ($p);
	if ($p =~ /check_/) {
	    push @selectedfields, ($localparam);
	} elsif ($p =~ /input_/) {
	    if (length ($localparam)) {
		$npreds++;
		$tmppred = $p;
		$tmppred =~ s/input_//;
		$predicates{$tmppred} = $localparam;
	    }
	}
    }
    $querystring = 'select ';
    for (my $i = 0; $i <= $#selectedfields; $i++) {
	$querystring .= $selectedfields[$i] . ', ' if $i < $#selectedfields;
	$querystring .= $selectedfields[$i] . ' ' if $i == $#selectedfields;
    }

    # No fields selected by user, so select all of them in query.
    if ($#selectedfields == -1) {
	$querystring .= ' * ';
    }

    $querystring .= "from $table";
    $querystring .= ' where (' if $npreds;
    foreach my $k (keys %predicates) {
	$querystring .= "$k " . $predicates{$k} . ' and ';
    }
    # remove the final 'and'
    $querystring =~ s/ and $// if $npreds;
    $querystring .= ')' if $npreds;
    $querystring .= ';';
    return $querystring;
}

sub starthtml {
    print $q -> header;
    print $styleheader;
    print qq|<body bgcolor="white" text="black">|;
}

sub endhtml {
    print qq|</body>|;
    print $q -> end_html;
}

sub get_fields {
    my ($userparam, $passwordparam, $hostparam, $dsnparam, $tableparam) =
	@_;
    my ($r, $rerror, $evh, $cnh, $sth, $text, $ncols, $nrows, $native);
    my ($name, $namelength, $type, $size, $decimal_digits, $nullable);
    my ($sqlstate, $textlen);
    my ($serverlogin, $serverpassword) = 
	split /\:\:/, $peers{$hostparam};
    my @lfields;
    my $client = 
	eval { RPC::PlClient->new('peeraddr' => $host,
				  'peerport' => $peerport,
				  'application' => 'RPC::PlServer',
				  'version' => $UnixODBC::VERSION,
				  'user' => $serverlogin,
				  'password' => $serverpassword) }
    or print "Failed to make first connection: $@\n";
    my $c = $client -> ClientObject ('BridgeAPI', 'new');

    if (ref $c ne 'RPC::PlClient::Object::BridgeAPI') {
	print "Error: Could not create network client.";
	print "Refer to the system log for the server error message.";
    }
    $evh =  $c -> sql_alloc_handle ($SQL_HANDLE_ENV, $SQL_NULL_HANDLE);
    if (defined $evh) { 
	$r = $c -> 
	    sql_set_env_attr ($evh, $SQL_ATTR_ODBC_VERSION, $SQL_OV_ODBC2, 0);
    } else {
	($rerror, $sqlstate, $native, $text, $textlen) = 
	    $c -> sql_get_diag_rec ($SQL_HANDLE_ENV, $evh, 1, 255);
	&client_error (0, 'sql_alloc_handle evh', $text);
	return 1;
    }
    $cnh = $c -> sql_alloc_handle ($SQL_HANDLE_DBC, $evh);
    if (! defined $cnh) {
	($rerror, $sqlstate, $native, $text, $textlen) = 
	    $c -> sql_get_diag_rec ($SQL_HANDLE_ENV, $evh, 1, 255);
	&client_error (0, 'sql_alloc_handle cnh', $text);
	return 1;
    }
    $r = $c -> sql_connect ($cnh, $dsn, length($dsnparam),
			    $user, length($userparam), 
			    $password, length($passwordparam));
    if ($r != 0) {
	($rerror, $sqlstate, $native, $text, $textlen) = 
	    $c -> sql_get_diag_rec ($SQL_HANDLE_DBC, $cnh, 1, 255);
	&client_error ($r, 'connect', $text);
    }

    $sth = $c -> sql_alloc_handle ($SQL_HANDLE_STMT, $cnh);
    if (! defined $sth) {
	($rerror, $sqlstate, $native, $text, $textlen) = 
	    $c -> sql_get_diag_rec ($SQL_HANDLE_DBC, $cnh, 1, 255);
	&client_error (0, 'sql_alloc_handle sth', $text);
    }

    $r = $c -> sql_columns ($sth, '', 0, '', 0,
			    $tableparam, length($tableparam), 
			    '', 0);
    if ($r != $SQL_SUCCESS) {
	($r, $sqlstate, $native, $text, $textlen) = 
	    $c -> sql_get_diag_rec ($SQL_HANDLE_STMT, $sth, 1, 255);
	&client_error (0, 'sql_columns', $text);
	return 1;
    }

    while (1) {
	$r = $c -> sql_fetch ($sth);
	last if $r == $SQL_NO_DATA;
	($r, $text, $textlen) = 
	    $c -> sql_get_data ($sth, 4, $SQL_C_CHAR, 255);
	if ($r != $SQL_SUCCESS) {
	    ($r, $sqlstate, $native, $text, $textlen) = 
		$c -> sql_get_diag_rec ($SQL_HANDLE_STMT, $sth, 1, 255);
	    &client_error (0, 'sql_get_data', $text);
	    return 1;
	} 
	push @lfields, ($text);
    }

    $r = $c -> sql_free_handle ($SQL_HANDLE_STMT, $sth);
    if ($r != 0) {
	($rerror, $sqlstate, $native, $text, $textlen) = 
	    $c -> sql_get_diag_rec ($SQL_HANDLE_DBC, $cnh, 1, 255);
	&client_error ($r, 'free_handle sth', $text);
    }

    $r = $c -> sql_disconnect ($cnh);
    if ($r != 0) {
	($rerror, $sqlstate, $native, $text, $textlen) = 
	    $c -> sql_get_diag_rec ($SQL_HANDLE_DBC, $cnh, 1, 255);
	&client_error ($r, 'disconnect', $text);
    }

    $r = $c -> sql_free_connect ($cnh);
    if ($r != 0) {
	($rerror, $sqlstate, $native, $text, $textlen) = 
	    $c -> sql_get_diag_rec ($SQL_HANDLE_ENV, $evh, 1, 255);
	&client_error ($r, 'free_connect cnh', $text);
    }

    $r = $c -> sql_free_handle ($SQL_HANDLE_ENV, $evh);
    if ($r != 0) {
	($rerror, $sqlstate, $native, $text, $textlen) = 
	    $c -> sql_get_diag_rec ($SQL_HANDLE_ENV, $evh, 1, 255);
	&client_error ($r, 'free_connect cnh', $text);
    }
    return @lfields;
}

sub doclientquery {
    my ($r, $rerror, $evh, $cnh, $sth, $text, $ncols, $nrows, $native);
    my ($name, $namelength, $type, $size, $decimal_digits, $nullable);
    my ($sqlstate, $textlen);
    my ($serverlogin, $serverpassword) = split /\:\:/, $peers{$host};
    my ($rc);
    my $client = 
	eval { RPC::PlClient->new('peeraddr' => $host,
				  'peerport' => $peerport,
				  'application' => 'RPC::PlServer',
				  'version' => $UnixODBC::VERSION,
				  'user' => $serverlogin,
				  'password' => $serverpassword) }
    or print "Failed to make first connection: $@\n";

    my $c = $client -> ClientObject ('BridgeAPI', 'new');

    if (ref $c ne 'RPC::PlClient::Object::BridgeAPI') {
	print "Error: Could not create network client.";
	print "Refer to the system log for the server error message.";
    }

    $evh =  $c -> sql_alloc_handle ($SQL_HANDLE_ENV, $SQL_NULL_HANDLE);
    if (defined $evh) { 
	$r = $c -> 
	    sql_set_env_attr ($evh, $SQL_ATTR_ODBC_VERSION, $SQL_OV_ODBC2, 0);
    } else {
	($rerror, $sqlstate, $native, $text, $textlen) = 
	    $c -> sql_get_diag_rec ($SQL_HANDLE_ENV, $evh, 1, 255);
	&client_error (0, 'sql_alloc_handle evh', $text);
	return 1;
    }

    $cnh = $c -> sql_alloc_handle ($SQL_HANDLE_DBC, $evh);
    if (! defined $cnh) {
	($rerror, $sqlstate, $native, $text, $textlen) = 
	    $c -> sql_get_diag_rec ($SQL_HANDLE_ENV, $evh, 1, 255);
	&client_error (0, 'sql_alloc_handle cnh', $text);
	return 1;
    }

    $r = $c -> sql_connect ($cnh, $dsn, length($dsn),
			    $user, length($user), 
			    $password, length($password));
    if ($r != 0) {
	($rerror, $sqlstate, $native, $text, $textlen) = 
	    $c -> sql_get_diag_rec ($SQL_HANDLE_DBC, $cnh, 1, 255);
	&client_error ($r, 'connect', $text);
    }

    $sth = $c -> sql_alloc_handle ($SQL_HANDLE_STMT, $cnh);
    if (! defined $sth) {
	($rerror, $sqlstate, $native, $text, $textlen) = 
	    $c -> sql_get_diag_rec ($SQL_HANDLE_DBC, $cnh, 1, 255);
	&client_error (0, 'sql_alloc_handle sth', $text);
    }

    # ODBC is particular about trailing whitespace, so remove it.
    $querytext =~ s/\;.*$/\;/msi;
    $r = $c -> sql_exec_direct ($sth, $querytext, length($querytext));
    if ($r != 0) {
	($rerror, $sqlstate, $native, $text, $textlen) = 
	    $c -> sql_get_diag_rec ($SQL_HANDLE_STMT, $sth, 1, 255);
	&client_error ($r, 'sql_exect_direct', $text);
    } else {
	($r, $ncols) = $c -> sql_num_result_columns ($sth);
	if ($r != 0) {
	    ($rerror, $sqlstate, $native, $text, $textlen) = 
		$c -> sql_get_diag_rec ($SQL_HANDLE_STMT, $sth, 1, 255);
	    &client_error ($r, 'sql_num_result_columns', $text);
	}

	# Get number of rows and columns in result set.

	($r, $nrows) = $c -> sql_row_count ($sth);
	if ($r != 0) {
	    ($rerror, $sqlstate, $native, $text, $textlen) = 
		$c -> sql_get_diag_rec ($SQL_HANDLE_STMT, $sth, 1, 255);
	    &client_error ($r, 'sql_row_count', $text);
	}
	print qq|<i>$nrows rows, $ncols columns in result set.</i><p>|;

	if (($nrows != 0) && ($ncols != 0)) {
	    # Get column descriptions
	    my $row = '<tr>';
	    &table_start;
	    foreach my $col (1..$ncols) {
		($r, $name, $namelength, $type, $size, $decimal_digits,
		 $nullable) = $c -> sql_describe_col ($sth, $col, 255);
		if ($r != 0) {
		    ($rerror, $sqlstate, $native, $text, $textlen) = 
			$c -> sql_get_diag_rec 
			    ($SQL_HANDLE_STMT, $sth, 1, 255);
		    &client_error ($r, 'sql_describe_col', $text);
		    last;
		}
		$row = "$row<td><b>$name</b></td>";
	    }
	    $row = "$row</tr>";
	    print $row;

	    while (1) {
		$r = $c -> sql_fetch ($sth);
		last if $r == $SQL_NO_DATA ;
		$row = '<tr>';
		foreach my $col (1..$ncols) {
		    ($r, $text, $textlen) = 
			$c -> sql_get_data ($sth, $col, 
					    $SQL_CHAR, 65536);
		    if ($r != 0) {
			($rerror, $sqlstate, $native, $text, $textlen) = 
			    $c -> sql_get_diag_rec 
				($SQL_HANDLE_STMT, $sth, 1, 255);
			&client_error ($r, 'sql_get_data', $text);
		    }
		    # This lets blank cells render correctly.
		    $text = '&nbsp;' if (!defined $text or 
					 (length ($text) == 0));
		    $row = "$row<td>$text</td>";
		}
		$row = "$row</tr>";
		print $row;
	    }
	    &table_end;
	}
    
	$r = $c -> sql_free_handle ($SQL_HANDLE_STMT, $sth);
	if ($r != 0) {
	    ($rerror, $sqlstate, $native, $text, $textlen) = 
		$c -> sql_get_diag_rec ($SQL_HANDLE_DBC, $cnh, 1, 255);
	    &client_error ($r, 'free_handle sth', $text);
	}

	$r = $c -> sql_disconnect ($cnh);
	if ($r != 0) {
	    ($rerror, $sqlstate, $native, $text, $textlen) = 
		$c -> sql_get_diag_rec ($SQL_HANDLE_DBC, $cnh, 1, 255);
	    &client_error ($r, 'disconnect', $text);
	}

	$r = $c -> sql_free_connect ($cnh);
	if ($r != 0) {
	    ($rerror, $sqlstate, $native, $text, $textlen) = 
		$c -> sql_get_diag_rec ($SQL_HANDLE_ENV, $evh, 1, 255);
	    &client_error ($r, 'free_connect cnh', $text);
	}

	$r = $c -> sql_free_handle ($SQL_HANDLE_ENV, $evh);
	if ($r != 0) {
	    ($rerror, $sqlstate, $native, $text, $textlen) = 
		$c -> sql_get_diag_rec ($SQL_HANDLE_ENV, $evh, 1, 255);
	    &client_error ($r, 'free_connect cnh', $text);
	}
	return 0;
    }
}

sub fieldform {
    my (@lfields) = @_;
    my $columns = $#lfields + 1;
    my ($input_val);
    print qq|<form action="/cgi-bin/tables.cgi">|;
    print $loginform;
    &table_start;
    print qq|<colgroup cols="$columns">\n|;
    print qq|<tr>\n|;
    foreach my $f (@lfields) {
	if ( length ($q -> param ("check_$f") ) ) {
	    print qq|<td><input type="checkbox" name="check_$f" value="$f" checked="1">$f</td>\n|;
	} else {
	    print qq|<td><input type="checkbox" name="check_$f" value="$f">$f</td>\n|;
	}
    }
    print qq|</tr>\n|;
    print qq|<tr>\n|;
    foreach my $f (@lfields) {
	if ( length ($q -> param ("input_$f") ) ) {
	    $input_val = $q -> param ("input_$f");
	    print qq|<td><input type="text" name="input_$f" value="$input_val"></td>\n|;
	} else {
	    print qq|<td><input type="text" name="input_$f" ></td>\n|;
	}
    }
    print qq|</tr>\n|;
    print qq|<tr>\n|;
    print qq|<td colspan="$columns">\n|;
    print qq|<input type="submit" name="submitquery" value="Submit Query">\n|;
    print qq|<input type="submit" name="gettextbox" value="Text Query">\n|;
    print qq|</td>\n|;
    print qq|</tr>\n|;
    print qq|</colgroup>\n|;
    &table_end;
    print qq|</form>|;
}

sub table_start {
    print qq|<table border="1">|;
}

sub table_end {
    print qq|</table>|;
}

sub client_error {
    my ($errno, $func, $text) = @_;
    print qq|<font size="5">Error</font><p>\n|;
    print qq|<pre>ODBC Error Code: $errno</pre><p>\n|;
    print qq|<pre>[$func]$text</pre>\n|;
}

sub readlogins {
    open LOGIN, $loginfile or die "Cannot open $loginfile: $!";
    my ($line, $host, $userpwd);
    while (defined ($line = <LOGIN>)) {
	next if $line =~ /^\#/;
	next if $line !~ /.*?::.*?::/;
	($host, $userpwd) = split /::/, $line, 2;
	$peers{$host} = $userpwd;
    }
    close LOGIN;
}

sub odbc_diag_message {
    my ($c, $handletype, $handle, $func, $unixodbcfunc) = @_;
    my ($rerror, $sqlstate, $native, $etext, $elength);
    ($rerror, $sqlstate, $native, $etext, $elength) = 
	$c -> sql_get_diag_rec ($handletype, $handle, 1, 255);
    return "[$func][$unixodbcfunc]$etext";
}
