import axios from "axios";

const api = axios.create({
    baseURL:"http:// 192.168.1.175:8000/api/"
});


api.interceptors.request.use(async(config)=>{

    const token = await AsyncStorage.getItem("token");

    if(token){
        config.headers.Authorization = `Bearer ${token}`;
    }

    return config;

});


export default api;