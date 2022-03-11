import TextField from '@mui/material/TextField';
import { useState } from "react";
export default function SearchField(props){
    function handleChange(e){
        props.parentCallback(e.target.value);
    }
    return(
        <TextField fullWidth id="standard-basic" label="Standard" variant="standard" onChange={handleChange}/>

    )
}