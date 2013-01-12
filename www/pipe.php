<?php
require_once('functions.php');

define('SOCKET_LOCATION', 'piper')

if($lastId = readGet('lastId')) {
	//Seems we know where to start in the list
	$time = time();
	while ((time() - $time) < 30) {
		try {
			$dbh = new PDO('mysql:host=localhost;dbname=mmc', 'mmc', 'mmc');
			$dbh->setAttribute( PDO::ATTR_ERRMODE, PDO::ERRMODE_WARNING );
			$sth = $dbh->prepare('SELECT * from log where id > ? ORDER BY id ASC LIMIT 100');
			$sth->execute(array($lastId));
			$sth->setFetchMode(PDO::FETCH_ASSOC);
			if($sth->rowCount() > 0) {
				# There's data, let's output it.
				$result = array_reverse($sth->fetchAll());
				$json = json_encode(array(
					'lastId' => @$result[0]['id'],
					'data' => array_reverse($result)
					));
				echo str_replace(array('<','>'), array('&lt;', '&gt;'), $json);
				break; # Break out of parent while-loop.
			}
		} catch(PDOException $e) {
			echo $e->getMessage();
			break;
		}
		usleep(25000); # Sleep a while before checking db again.
	}
} elseif($cmd = readGet('cmd')) {
	//There is a command to execute
	if ($socket = create_socket(AF_UNIX, SOCK_STREAM, 0) AND
		socket_connect($socket, SOCKET_LOCATION) ) {
		// Socket created and connected successfully, send data.
		$cmd = $cmd.'\n';
		socket_send($socket, $cmd, strlen($socket))
		socket_close($socket);
	} else {
		// Something went wrong, output error message.
		print socket_strerror(socket_last_error());
	}
} else {
	//Business as usual, output last lines from db.
	try {
		$dbh = new PDO('mysql:host=localhost;dbname=mmc', 'mmc', 'mmc');
		$dbh->setAttribute( PDO::ATTR_ERRMODE, PDO::ERRMODE_WARNING );
		$sth = $dbh->query('SELECT * from log ORDER BY id DESC LIMIT 100');
		$sth->setFetchMode(PDO::FETCH_ASSOC);
		$result = $sth->fetchAll();
		$json = json_encode(array(
			'lastId' => $result[0]['id'],
			'data' => array_reverse($result)
			));
		echo str_replace(array('<','>'), array('&lt;', '&gt;'), $json);
	} catch(PDOException $e) {
		echo $e->getMessage();
	}
	
}
#if (isset($_GET['cmd']) && !empty($_GET['cmd'])) {
#	$cmd = $_GET['cmd'];
/**	$pipe = fopen('piper','r+');
	while($f = fgets($pipe)) {
		echo $f;
	}
	fclose($pipe);
	#echo 'Sent command: '.$cmd;
#} else {
#	echo 'Move along.';
#}**/
?>
