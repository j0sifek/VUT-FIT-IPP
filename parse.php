<?php
#Global variables for instruction and comment counting 
$in_Number = 1;
$comentLines = 0;
$stats = 'no'; 
#Global array of instructions 
$instrInfo = array(
	'MOVE' => array(2, 'v', 's'),
	'CREATEFRAME' => array(0),
	'PUSHFRAME' => array(0),
	'POPFRAME' => array(0),
	'DEFVAR' => array(1, 'v'),
	'CALL' => array(1, 'l'),
	'RETURN' => array(0),
	'PUSHS' => array(1, 's'),
	'POPS' => array(1, 'v'),
	'ADD' => array(3, 'v', 's', 's'),
	'SUB' => array(3, 'v', 's', 's'),
	'MUL' => array(3, 'v', 's', 's'),
	'IDIV' => array(3, 'v', 's', 's'),
	'LT' => array(3, 'v', 's', 's'),
	'GT' => array(3, 'v', 's', 's'),
	'EQ' => array(3, 'v', 's', 's'),
	'AND' => array(3, 'v', 's', 's'),
	'OR' => array(3, 'v', 's', 's'),
	'NOT' => array(2, 'v', 's'),
	'INT2CHAR' => array(2, 'v', 's'),
	'STRI2INT' => array(3, 'v', 's', 's'),
	'READ' => array(2, 'v', 't'),
	'WRITE' => array(1, 's'),
	'CONCAT' => array(3, 'v', 's', 's'),
	'STRLEN' => array(2, 'v', 's'),
	'GETCHAR' => array(3, 'v', 's', 's'),
	'SETCHAR' => array(3, 'v', 's', 's'),
	'TYPE' => array(2, 'v', 's'),
	'LABEL' => array(1, 'l'),
	'JUMP' => array(1, 'l'),
	'JUMPIFEQ' => array(3, 'l', 's', 's'),
	'JUMPIFNEQ' => array(3, 'l', 's', 's'),
	'DPRINT' => array(1, 's'),
	'BREAK' => array(0),
);

#Def. of functions:

#Takes instruction  prints it in XML on STDOUT
function xmlInstruction($arguments,  $typeoOfArg) {
	global $in_Number;
	echo "<instruction order=\"$in_Number\" opcode=\"$arguments[0]\">";
	for($j, $i = 1; $i < count($arguments); $i++){
		$j = $i -1;
		#Xml symb. compatibility
		$arguments[$i] = preg_replace('/</','&lt;',$arguments[$i] );
		$arguments[$i] = preg_replace('/>/','&gt;',$arguments[$i] );
		$arguments[$i] = preg_replace('/&/','&amp;',$arguments[$i] );
		$arguments[$i] = preg_replace('/\"/','&quot;',$arguments[$i] );
		$arguments[$i] = preg_replace('/\'/','&quot;',$arguments[$i] );
		echo"<arg$i type=\"$typeoOfArg[$j]\">$arguments[$i]</arg$i>";
	}
	echo "</instruction>";
	$in_Number++;
}
 
#Takes instruction and checks if it is valid
function instrValidate($instr) {
	global $instrInfo;
	if(array_key_exists($instr[0],$instrInfo)){
		if(count($instr)-1 == $instrInfo[$instr[0]][0]){
			paramValidate($instr);
		}else{
			error_log("Wrong ammount of parametres\n");
			exit(21);
			}
	}else{
		error_log("Unknown instruction $instr[0]\n");
		exit(21);
	}
}

#Checks if the parameters are valid
function paramValidate($instr) {
	global $instrInfo;
	$typeoOfArg = array();
	for($i = 1; $i <= $instrInfo[$instr[0]][0]; $i++){
			$type= $instrInfo[$instr[0]][$i];
			if($type == 'v'){
				if( !preg_match('/^(LF@|GF@|TF@)[A-Za-z_\-$&%*]{1}[A-Za-z0-9_\-$&%*]*$/', $instr[$i])){
					error_log("Wrong name of variable\n"); 
					exit(21);}
				else{
					array_push($typeoOfArg, "var");
				}			
			}
			if($type == 's'){ 
				if(preg_match('/^(LF@|GF@|TF@)[A-Za-z_\-$&%*]{1}[A-Za-z0-9_\-$&%*]*$/', $instr[$i])){
					#isVar
					array_push($typeoOfArg, "var");
				}else if(preg_match('/^int@-{0,1}\+{0,1}[0-9]+$/', $instr[$i])){
					#is int 
					array_push($typeoOfArg, "int");
					$instr[$i] = preg_replace('/int@/','',$instr[$i] );
				}else if(preg_match('/^bool@(true|false)$/', $instr[$i])){
					#is bool 
					array_push($typeoOfArg, "bool");
					$instr[$i] = preg_replace('/bool@/','',$instr[$i] );
				}else if(preg_match('/^string@.*$/', $instr[$i])){
					#is string 
					array_push($typeoOfArg, "string");
					$instr[$i] = preg_replace('/string@/','',$instr[$i] );
				}else if(preg_match('/^[A-Za-z_\-$&%*]{1}[A-Za-z0-9_\-$&%*]*$/', $instr[$i])){
					#is label 
					array_push($typeoOfArg, "label");
				}else{
					error_log("Invalid symbol \"$instr[$i]\"\n"); 
					exit(21);
				}			
			}
			if($type == 'l'){
				if( !preg_match('/^[A-Za-z_\-$&%*]{1}[A-Za-z0-9_\-$&%*]*$/', $instr[$i])){
					error_log("Wrong name of label\n"); 
					exit(21);}
				else{
					array_push($typeoOfArg, "label");
				}		
			}
			if($type == 't'){
				$types = array('int', 'bool', 'string');
				if(in_array($instr[$i], $types)){
					array_push($typeoOfArg, "type");
				}else{
					error_log("Wrong wrong wrong. \n"); 
					exit(21);}	
			}
	}
	#params OK
	xmlInstruction($instr, $typeoOfArg);	
}
##############################-Parameters-###############################
$longopts = array("help", "stats::", "comments", "loc",);
$options = getopt("", $longopts);

if(array_key_exists("help" , $options)){
	if($argc != 2)
		exit(10);
	echo"Runin this script with IPP input and you will get IPP output";
	exit(0);
}

if(array_key_exists("stats" , $options)){

	$statsLocation = $options["stats"];

	if(array_key_exists("comments" , $options) ){
		$stats = 'co';
		if(is_array($options["comments"]))
			exit(10);
	}


	if(array_key_exists("loc" , $options) ){
		$stats = 'lo';
		if(is_array($options["loc"]))
			exit(10);
	}

	if((array_key_exists("loc" , $options)) && (array_key_exists("comments" , $options)  )){
		
		if($argv[1] == '--comments'){
			$stats = 'cl';
		}
		if($argv[3] == '--comments'){
			$stats = 'lc';
		}
		if($argv[1] == '--loc'){
			$stats = 'lc';
		}
		if($argv[3] == '--loc'){
			$stats = 'cl';
		}

	} 

	
}else{
	if((array_key_exists("loc" , $options)) || (array_key_exists("comments" , $options)  )){
		error_log("Missing parameter\n"); 
		exit(10);
	} 
}

if($argc > 4)
	exit(10);

#Begining of the program


#Check if it is headder, and its correct one
$line = fgets(STDIN);
$comments = $line;
$line = preg_replace('/#.*/','',$line);
	if($line != $comments)
		$comentLines++;
$line = preg_replace('/\s+/','',$line);
$lineU = strtoupper($line);
if(  !preg_match('/^\.IPPCODE18$/',$lineU) ){
	error_log("Missing header\n"); 
	exit(21);
}
$out = substr($line, 0, -1);
echo"<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n";
echo "<program language=\"IPPcode18\">";
 
#Reading lines one by one to the end
while($line = fgets(STDIN)){
	$comments = $line;
	$line = preg_replace('/#.*/','',$line);
	if($line != $comments)
		$comentLines++;

	if(preg_match('/^\s*$/',$line) == 0){
		$line = preg_replace('/^\s+/','',$line);
		$words   = preg_split('/\s+/', $line);	
		if(end($words) == '')
			array_pop($words);
		$words[0] = strtoupper($words[0]);
		instrValidate($words);
	}
}

echo "</program>";

#Bonus statistics
if($stats != 'no'){
	$in_Number--;
	$statfile = fopen($statsLocation, "w");
	if($stats[0] == 'l')
		fwrite($statfile, "$in_Number\n");
	if($stats[0] == 'c')
		fwrite($statfile, "$comentLines\n");
	if($stats[1] == 'l')
		fwrite($statfile, "$in_Number\n");
	if($stats[1] == 'c')
		fwrite($statfile, "$comentLines\n");
	fclose($statfile);

}
?>
