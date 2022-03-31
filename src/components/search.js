import React from 'react';
import TextField from '@mui/material/TextField';

export default function SearchField(props){
    function handleChange(e){
        props.parentCallback(e.target.value);
    }
    console.log(window.location);
    return(
        <TextField fullWidth id="standard-basic" label={props.text} error = {props.error} variant="standard" onChange={handleChange} defaultValue={props.initialvalue}/>

    )
}