import React from 'react';
import Button from '@mui/material/Button';
import ButtonGroup from '@mui/material/ButtonGroup';


export default function PageButton(props){

    if (!props.show){
        return null
    }
    if(props.numResults < 10 && props.pagenum === 1){
        console.log("wacaoooo");
        return null;
    }
    return(
        <ButtonGroup variant="contained" aria-label="outlined primary button group">
            <Button disabled= {props.disableback} onClick = {() => {
                if(props.pagenum !== 1){
                    props.sexyProp(props.pagenum-1);
                }
            }}> {"<"} </Button>
            <Button>Page {props.pagenum +""}</Button>
            <Button disabled = {(props.numResults < 10)}
                onClick={() => {
                props.sexyProp(props.pagenum + 1);
            }}> {">"} </Button>
        </ButtonGroup>
    )
}