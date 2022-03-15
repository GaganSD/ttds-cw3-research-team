import React, { Component } from 'react';
import Button from '@mui/material/Button';

export default function SearchButton(props){
    return(
        <Button variant="contained" onClick = {() => {
            props.parentCallback();
        }

        }>
            ㅤSearch Queryㅤ
        </Button>

    );
}