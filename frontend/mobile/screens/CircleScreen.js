import React,{useEffect,useState} from "react";
import {
View,
Text,
Button
}
from "react-native";

import api from "../api/api";


export default function CircleScreen(){

const [round,setRound]=useState(null);


useEffect(()=>{

loadRound();

},[]);



const loadRound=async()=>{

// temporary until you create GET round API

console.log("Load circle");

}



const contribute=async()=>{

await api.post(
"rounds/contribute/",
{
round_id:1
}
);


alert("Contribution done");

}



return(

<View>

<Text>
Circle Fund
</Text>


<Button
title="Contribute"
onPress={contribute}
/>


</View>

)


}