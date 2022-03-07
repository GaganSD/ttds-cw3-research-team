import Button from '@mui/material/Button';

export default function SearchButton(){
    return(
        <Button variant="contained" color="success" onClick = {() => {
            alert('clicked');
        }

        }>
            Search
        </Button>

    );
}