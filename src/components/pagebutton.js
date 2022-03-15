import React from 'react';
import Button from '@mui/material/Button';
import ButtonGroup from '@mui/material/ButtonGroup';
import { react } from '@babel/types';


export default function PageButton(props){
    const [pagenum, setPageNum] = React.useState(1);
    const [gobackbuttondisabled, setGoBackButtonDisabled] = React.useState(true);
    React.useEffect(() =>{
        if(pagenum === 1){
            setGoBackButtonDisabled(true);
        }
        else{
            setGoBackButtonDisabled(false);
        }

    },[pagenum]);
    if(props.show === false){
        return null;
    }

    return(
        <ButtonGroup variant="contained" aria-label="outlined primary button group">
            <Button disabled= {gobackbuttondisabled} onClick = {() => {
                if(pagenum !== 1){
                    setPageNum(pagenum-1);
                }
            }}> {"<"} </Button>
            <Button>Page {pagenum +""}</Button>
            <Button onClick={() => {
                setPageNum(pagenum + 1);
            }}> {">"} </Button>
        </ButtonGroup>
    )
}