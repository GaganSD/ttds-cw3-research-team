import TextField from '@mui/material/TextField';
import { useState } from "react";
export default function SearchField(){
    const [search, setSearch] = useState('');
    function handleChange(e){
        console.log(e.target.value);
    }
    return(
        <TextField id="standard-basic" label="Standard" variant="standard" onChange={handleChange}/>

    )
}