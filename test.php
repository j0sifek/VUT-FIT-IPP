<?php
############################-Global variables-########################
$path = '.'; #Where to run the script
$parser_location = substr(shell_exec("pwd"), 0, -1);
$interpret_location = $parser_location;

################################-Functions-############################

function singleTest($testName) {

	global $parser_location;
	global $interpret_location;
	global $path;

	$retVal = shell_exec("php \"$parser_location/parse.php\" <\"$path/$testName.src\" 1>\"$testName.tmpa\" 2>/dev/null; echo $?");
	$retVal = intval($retVal);

	if($retVal != 0){
		scriptFail($testName, $retVal);
		shell_exec("rm \"$testName.tmpa\"");
		return;
	}

	$retVal = shell_exec("python3 \"$interpret_location/interpret.py\" --source=\"$testName.tmpa\" <\"$path/$testName.in\" 1>\"$testName.tmpb\" 2>/dev/null; echo $?");

	shell_exec("rm \"$testName.tmpa\"");
	
	$retVal = intval($retVal);
	if($retVal != 0){
		scriptFail($testName, $retVal);
		shell_exec("rm \"$testName.tmpb\"");
		return;
	}
	#Interpret finished, check retavl
	if( file_exists("\"$path/$testName.rc\"")){
		$myfile = fopen("\"$testName.rc\"", "r");
		$retvalRef = fgets($myfile);
		$retvalRef = intval($retvalRef);
		if ($retvalRef != $retVal){
			testHtmlOut($testName, $retVal, $retvalRef, false); 
			shell_exec("rm \"$testName.tmpb\"");
			return;
		}
	}
	#If evrything is ok, diff the outputs	
	# -N   treat absent files as empty

	$diffOut = shell_exec("diff -N \"$path/$testName.out\" \"$testName.tmpb\"");
	if($diffOut == ''){
		testHtmlOut($testName, 0, 0, true); #echo "Test passed. Results match.\n";
	}else{
		testHtmlOut($testName, 0, 0, false); #echo "Test failed. Results DO NOT match.\n";
	}
	shell_exec("rm \"$testName.tmpb\"");
}

function scriptFail($testName, $retVal){

	if( !file_exists("$testName.rc")){
	//if( !shell_exec("[ -f \"$testName.rc\" ] && echo 1 || echo 0")){
		testHtmlOut($testName, $retVal, 0, false); #echo "Test failed. Return code not found thus expected 0 got $retVal.\n";
	}else{
		$myfile = fopen("$testName.rc", "r");
		$retvalRef = fgets($myfile);
		if ($retvalRef == $retVal){
			testHtmlOut($testName, $retVal, $retvalRef, true); #echo "Test passed, return codes match.\n";	
			return;
		}
		else
			testHtmlOut($testName, $retVal, $retvalRef, false); #echo"Test failed. Expected retval $retvalRef got $retval\n";
	}
}

function htmlStart(){
	echo 
	"	<html>
	<head>
	<title>IPP Tests</title>
	</head> 
	<br><center><b><font size=\"8\"> IPP TESTS</font> </b></center><br>
	<table style=\"width:45%\" align=\"center\">
	<tr>
	<th>Test Name</th>
	<th>Return code</th>
	<th>Expected RC</th> 
	<th>Succes</th>
	</tr>\n\n";
}

function htmlEnd(){
	echo 
	"\n	<html>
	</table>
	</body>
	</html>\n";	
}

function testHtmlOut($testName, $rc, $erc, $succ){
	$color = $succ ? "#8ff442":"#f2602b";
	$succ = $succ ? "Yes":"No";
	echo"
	<tr align=\"center\" bgcolor=\"$color\"> 
	<td>$testName</td>
    <td>$rc</td> 
    <td>$erc</td>
    <td>$succ</td>
	</tr>\n";	
}

##############################-Parameters-###############################
$longopts = array("help", "directory::", "recursive", "parse-script::", "int-script::",);
$options = getopt("", $longopts);

if(array_key_exists("help" , $options)){
	echo"Runing this cript will automaticaly run ale tests in current folder.\n --directory=* changes the folder\n --recursive goes to subfolders\n --parse-script=* path to parse script \".\" by default \n --int-script=* path to int script \".\" by default\n";
	exit(0);
}

if(array_key_exists("directory" , $options))
	$path = $options["directory"];
#shell_exec("cd $path");

if(array_key_exists("recursive" , $options)){
	$testsShell = shell_exec("find $path -type f |grep .src$");
	}else{
		$testsShell = shell_exec("ls $path |grep .src$");
	}

if(array_key_exists("parse-script" , $options)){
	$parser_location = $options["parse-script"];
	}

if(array_key_exists("int-script" , $options)){
	$interpret_location = $options["int-script"];
	}


########################-Begining of the program-########################

#Run parse.php, foreach - test.src as input
$tests = explode("\n", $testsShell);
array_pop ($tests);	#Removes blankline	

htmlStart();

foreach ($tests as $test){
	singleTest(preg_replace('/.src$/','',$test));
}
htmlEnd();
?>
