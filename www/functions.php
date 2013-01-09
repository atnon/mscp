<?php

function readGET($name) {
	if(isset($_GET[$name]) && !empty($_GET[$name])) {
		return $_GET[$name];
	} else {
		return Null;
	}
}
