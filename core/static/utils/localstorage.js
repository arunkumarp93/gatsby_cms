export default class LocalStorage{

  static jsonConverter(value, parse=false){
    return parse ? JSON.parse(value) : JSON.stringify(value)
  }

  static getAllContents(){
    return Object.keys(localStorage)
  }

  static clearAll(){
     localStorage.clear()
  }

  static getData(key){
    return LocalStorage.jsonConverter(localStorage.getItem(key), true)
  }
  setData(key, data){
     try{
       localStorage.setItem(key, LocalStorage.jsonConverter(data))
     }
     catch(err){
       console.log(err)
       localStorage.removeItem(key)
     }
  }
}
