<!DOCTYPE html>
<html lang='en'>
<head>
	<meta charset='utf-8' />
	<title>MSCP</title>
	<link href='http://fonts.googleapis.com/css?family=Monda' rel='stylesheet' type='text/css' />
	<style>
	* { font-family: 'Courier', sans-serif; font-size: 14px; }
	html,body {
		width:	100%;
        height: 100%;
		margin: 0px;
		padding: 0px;
	}
	.header {
		position: absolute;
		top: 0px;
		left: 0px;
		width: 100%;
		margin: 0px;
		background-color: #364b18;
		opacity: 0.95;
		border: none;
		border-bottom: 1px solid black;
        z-index: 9999;
	}
	.contentpane {
		width: 100%;
		margin: 0px;
		padding: 0px;
		color: #fff;
		background-color: #333;
		height: 100%;
        top: 0px;
        bottom: 0px;
        overflow: hidden; /*FIXME: Dirty trick. Upper scrollbar arrow gets clipped. */
	}
	h1 {
		font-size: 1.5em;
		font-family: 'Monda', sans-serif;
		line-height: 10px;
        padding-left: 0.5em;
        color: white;
	}
    .cmdLine {
        position: relative;
        padding: 0px;
        margin: 0px;
        width: 100%;
        height: 1.5em;
        background-color: inherit;
        border-top: 1px solid black;
        bottom: 0px;
        line-height: 1.5em;
    }
	#cmd {
		padding: 0px;
		margin: 0px;
		float: left;
		right: 0px;
		width: 90%;
		border: none;
		height: inherit;
		background-color: inherit;
		color: inherit;
		outline: none;
		line-height: inherit;
	}
    #cmdHead {
        position: relative;
        float: left;
        padding: 0px;
        margin: 0px;
        padding-left: 0.5em;
        height: inherit;
        background-color: inherit;
        line-height: inherit;
	}
    .logContainer {
        position: relative;
        overflow-y: scroll;
        margin: 0px;
        padding: 0px;
        width: 100%;
        height: 100%;
    }
	table {
        width: 100%;
	}
	tr:nth-child(even) { background: #404040; }
	td { padding-left: 0.5em; }
	.INFO { color: green; }
	.WARNING { color: yellow; }
	.SEVERE { color: red; }
	.UNKNOWN { color: white; }
	</style>
</head>
<body>
	<script src="//ajax.googleapis.com/ajax/libs/jquery/1.8.3/jquery.min.js"></script>
	<script>
		var lastRecId = '';
		function addText(text) {
			var obj = $('#log');
			obj.append(text);
			//obj.scrollTop(obj[0].scrollHeight);	
			$('.logContainer').scrollTop($('.logContainer')[0].scrollHeight); // Scroll to bottom
		}
		function sendCmd(command) {
			$.get('pipe.php', {cmd: command});
		}
		function updateLog() {
			$.getJSON('pipe.php', {lastId: lastRecId}, function(json) {
				if(json != null && json.lastId) {
					lastRecId = json.lastId;
					console.log(json);
					var obj = null;
					var resLine = '';
					for(var i = 0; i<json.data.length; i++) {
						obj = json.data[i]; 
						resLine += '<tr class="logLine"><td>';
						resLine += obj.date+' ';
						resLine += obj.time+' ';
						resLine += '[<span class="'+obj.level+'">'+obj.level+'</span>] ';
						resLine += obj.message;
						resLine += '</td></tr>';
					}
					addText(resLine);
				} else { }
				updateLog(); //Rinse and repeat, serverside uses long polling.
			})
		}

		// Command history
		var cmdHist = new function() {
			this.history = [];
			this.currentIndex = -1;
			this.add = function (line) {
				this.history.unshift(line); // Add line to stack.
				this.currentIndex = -1; // Reset pointer.
				return ''; // Return empty line.
			};
			this.back =  function () {
				if (this.currentIndex < this.history.length-1) {
					this.currentIndex++; // Increase pointer
				}
				console.log('curInd: '+this.currentIndex);
				return this.history[this.currentIndex]; // Return commandline.
			};
			this.forward = function () {
				if(this.currentIndex > 0) {
					this.currentIndex--;
					return this.history[this.currentIndex];
				} else {
					this.currentIndex = -1;
					return '';
				}
			};
		};
				

		$(document).ready(function () {
			var history = [];
			$('.logContainer').scrollTop($('.logContainer')[0].scrollHeight); // Scroll to bottom
			//setInterval("updateLog()", 200);
			updateLog(); // This will run the whole session, triggering itself.
			$('#cmd').focus(); // Set focus on cmdline
			$('#cmd').keydown(function(event) {
				// 13 = Enter
				if(event.which == 13 && $('#cmd').val() != '') {
					event.preventDefault();
					sendCmd($('#cmd').val());
					$('#cmd').val(cmdHist.add($('#cmd').val()));
				
				}
				//38 = UpArrow
				if(event.which == 38) {
					event.preventDefault();
					$('#cmd').val(cmdHist.back());
				}
				//40 = DownArrow
				if(event.which == 40) {
					event.preventDefault();
					$('#cmd').val(cmdHist.forward());
				}	
			});
		});
	</script>
	<div class='header'><h1>MSCP</h1></div>
	<div class='contentpane'>
	<div class='logContainer'>
        <table id="log">
        </table>
    </div>
	<div class="cmdLine"><label for='cmd' id="cmdHead">MSCP>&nbsp;</label><input id='cmd' type='text' /></div>
	</div>
</body>
</html>
