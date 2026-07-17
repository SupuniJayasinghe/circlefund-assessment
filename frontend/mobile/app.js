import React from "react";

import {
NavigationContainer
}
from "@react-navigation/native";


import {
createNativeStackNavigator
}
from "@react-navigation/native-stack";


import LoginScreen from "./screens/LoginScreen";
import CircleScreen from "./screens/CircleScreen";


const Stack=createNativeStackNavigator();


export default function App(){

return(

<NavigationContainer>

<Stack.Navigator>

<Stack.Screen
name="Login"
component={LoginScreen}
/>


<Stack.Screen
name="Circle"
component={CircleScreen}
/>


</Stack.Navigator>

</NavigationContainer>

)

}