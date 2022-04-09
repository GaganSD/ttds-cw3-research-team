import React from 'react';
import Button from '@mui/material/Button';

export default function QueryExpansionButton(props){
    return(
        <Button title="Get Query Expansion" variant="contained" style={{display: 'flex', justifyContent: 'center'}} onClick = {() => {
            props.parentCallback();
        }}>EXPAND</Button>
    );
}