import React,{useState} from "react";
import {View,TextInput,Button,Alert} from "react-native";
import api from "../api/api";
import AsyncStorage from "@react-native-async-storage/async-storage";


export default function LoginScreen({navigation}){

const [username,setUsername]=useState("");
const [password,setPassword]=useState("");


const login=async()=>{

try{

const response=await api.post(
"login/",
{
username,
password
}
);


await AsyncStorage.setItem(
"token",
response.data.access
);


navigation.replace("Circle");


}catch(error){

Alert.alert(
"Login failed",
"Invalid credentials"
);

}

}


return(

<View>

<TextInput
placeholder="Username"
onChangeText={setUsername}
/>


<TextInput
placeholder="Password"
secureTextEntry
onChangeText={setPassword}
/>


<Button
title="Login"
onPress={login}
/>


</View>

)

}