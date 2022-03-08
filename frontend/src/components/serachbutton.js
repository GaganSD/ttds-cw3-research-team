import Button from '@mui/material/Button';

export default function SearchButton(props){
    return(
        <Button variant="contained" color="success" onClick = {() => {
            props.parentCallback();
        }

        }>
            Search
        </Button>

    );
}