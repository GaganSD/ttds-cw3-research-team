import { Box } from '@mui/system';
import { useParams } from 'react-router-dom'
import research_logo from '../logos/Re-Search-logos_transparent.png';
import SearchField from './search';
import SearchButton from './SearchButton';
import SettingsSuggestIcon from '@mui/icons-material/SettingsSuggest';
import IconButton from '@mui/material/IconButton';
import { Button } from '@mui/material';

export default function ResultsPage(props){
    const {query,df,dt,alg,srchtyp,ds,pn} = useParams();
    console.log(query);
    console.log(df);
    console.log(df);
    // console.log(category);

    return(
        <div className='ResultsPage'>
            <div className='searchBar'>
                <Box
                sx={{
                    width:'100%',
                    height:"5em",
                    backgroundColor: 'grey'
                }}>
                    <div style={{display:'flex',
                flexDirection:'row',
                justifyContent:'center'}}>
                        <div className='Options' style={{
                            marginRight : '10em',
                            marginTop: '1.5em'
                        }}> 
                            <Button variant="contained" size="small" startIcon={<SettingsSuggestIcon/>}>
                                Options
                            </Button>
                        </div>
                        <h1>Re-Search</h1>
                        <div className='SearchField' style={{width:'30%',
                    marginTop:'1.5em',
                    marginLeft:'1em'}}>
                            <SearchField sx={{width:'50%'}}/>
                        </div>
                        <div className='SearchButton' style={{
                            marginTop:'1.5em',
                            marginLeft:'1em'
                        }}>
                            <SearchButton/>
                        </div>
                    </div>
                </Box>
                <p>moneybag yo</p>
            </div>
        </div>
    )
}