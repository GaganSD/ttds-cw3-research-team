import * as React from 'react';
import { Box } from '@mui/system';
import { useParams } from 'react-router-dom'
import SearchField from './search';
import { Button } from '@mui/material';
import SwipeableTemporaryDrawer from './advancedOptionsResultsPage';
import PaperOrDS from './datasetorpaperresultspage';
import ButtonGroup from '@mui/material/ButtonGroup';
import QEButton from './QueryExpansionButton';
import PageButton from './pagebutton';
import research_logo_side from '../logos/researchlogoside.png';
import 'typeface-roboto';
import { createTheme, ThemeProvider } from '@mui/material/styles';
import '@fontsource/roboto/300.css';
import '@fontsource/roboto/400.css';
import '@fontsource/roboto/500.css';
import '@fontsource/roboto/700.css';


export default function ResultsPage(props) {
    const backend_server_ip = "http://34.145.46.81:5000/";

    const routeChange = () => {

        if (search === '' || !/^(?!\s+$).+/.test(search)) {
        }
        else if (search.length >16){
            setLongQuery(true);
        }
        else if (!/^[0-9a-zA-Z\s]*$/.test(search)) {
            setBadQuery(true);

        }
        else {

            let path = create_url(search, values.current);
            window.location = (window.location.origin + '/' + path);
        }
    }
    const { query, df, dt, alg, srchtyp, ds, pn } = useParams();
    const query_spaced = query.replaceAll('+', ' ');
    React.useEffect(() => {
        if (df === "inf") {
            values.current.range_from = null;
        }
        else {
            values.current.range_from = new Date(df)
        }
        if (dt === "inf") {
            values.current.range_to = null;
        }
        else {
            values.current.range_from = new Date(dt)
        }

        let search_query = formaturl(window.location.pathname);

        return fetch(backend_server_ip + search_query).then(response => response.json()).then(data => {
            if (data.Results.length === 0) {
                setEmptyResults(true);
            }
            else {
                setBadQuery(false);
                setEmptyResults(false);
                showPageButton.current = true;
                setJsonResults(data);
            }
        })
    }, []);


    const theme = createTheme({

        components: {
            MuiTypography: {
                defaultProps: {
                    variantMapping: {
                        h1: 'h2',
                        h2: 'h2',
                        h3: 'h2',
                        h4: 'h2',
                        h5: 'h2',
                        h6: 'h2',
                        subtitle1: 'h2',
                        subtitle2: 'h2',
                        body1: 'span'

                    ,
                        body2: 'span',
                    },
                },
            },
        },
    });



    const [search, setSearch] = React.useState(query_spaced);
    const showPageButton = React.useRef(false);
    const [pagenum, setPageNum] = React.useState(parseInt(pn));
    const [datasets, setDatasets] = React.useState((ds === "true"));
    const [badquery, setBadQuery] = React.useState(false);
    const [emptyresults, setEmptyResults] = React.useState(false);
    const [longquery, setLongQuery] = React.useState(false);
    const gobackbuttondisabled = (pn==="1") ? true: false;
    const [json_results, setJsonResults] = React.useState({ "Results": [] });
    const [json_query_expansion, setJsonQE] = React.useState({ QEResults: [] });
    const [pods_text, setpodsText] = React.useState((ds === "true") ? "DataSets" : "Papers");
    const values = React.useRef({
        algorithm: alg,
        searchtype: srchtyp,
        range_from: new Date(df),
        range_to: new Date(df),
        datasets: ds,
        pagenum: parseInt(pn)
    });

    const formaturl = (unformatted_url) => {
        let options = unformatted_url.split("/");
        let formatted_url = "";
        formatted_url += options[1] + "?q=";
        formatted_url += options[2] + "/df=";
        formatted_url += options[3] + "/dt=";
        formatted_url += options[4] + "/alg=";
        formatted_url += options[5] + "/srchtyp=";
        formatted_url += options[6] + "/ds=";
        formatted_url += options[7] + "/pn=";
        formatted_url += options[8] + "/";

        return formatted_url;

    };

    function standardize_dates(string_date) {

        string_date = string_date.replaceAll('-', '/');
        string_date = string_date.replace(/\s+/g, "");

        var _format = "d/m/y"
        var formatItems = _format.split('/');
        var dateItems = string_date.split('/');
        var dayIndex = formatItems.indexOf("d");
        var monthIndex = formatItems.indexOf("m");
        var yearIndex = formatItems.indexOf("y");

        var yr = parseInt(dateItems[yearIndex]);
        var year;
        if (yr < 100 && yr <= 21) { //handling 2 digit years
            year = "20" + yr;
        } else if (yr < 100) {
             year = "19" + yr;
        } else {
            year = yr;
        }

        if (isNaN(dateItems[monthIndex])) { //in case the month is written as a word
            var d = new Date(string_date);
        } else {

            var month = parseInt(dateItems[monthIndex]);
            month -= 1;

            var d = new Date(year, month, dateItems[dayIndex]);
        }

        const monthNames = ["January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December"];
        let formatted = monthNames[d.getMonth()] + ", " + d.getFullYear();

        if (formatted === "undefined, NaN") {
            return "";
        }

        return " • " + formatted;
    }
    // check if this works or else remove this.
    var isMobile = /iPhone|iPad|iPod|Android/i.test(navigator.userAgent);

    function abstractgenerator(text) {

        if (text !== "") {
            if (isMobile) {
                if (text.length > 100) {
                    return text.substring(0, 100) + "...";
                }
            } else {
                if (text.length > 500) {
                    return text.substring(0, 500) + "...";
                }
            }
        }
    }

    function authorlist(authors) {
        var lower = authors.toLowerCase()
        if (authors.includes(",")) {
            return " • " + authors;
        } else if (!(lower == "n/a" || lower == "na" || lower == "NA"
            || lower == "n-a" || lower == "" || lower == " ")) {
            return " • " + authors;
        }
    }
    function fix_url(raw_url) {
        var domain = extractHostname(raw_url),
            splitArr = domain.split('.'),
            arr_len = splitArr.length;

        if (arr_len > 2) {
            domain = splitArr[arr_len - 2] + '.' + splitArr[arr_len - 1];
            //check to see if it's using a Country Code Top Level Domain (ccTLD) (i.e. ".me.uk")
            if (splitArr[arr_len - 2].length == 2 && splitArr[arr_len - 1].length == 2) {
                //this is using a ccTLD
                domain = splitArr[arr_len - 3] + '.' + domain;
            }
        }
        return domain;
    }

    function QueryExpansion() {

        return fetch(backend_server_ip + 'QE/' + search).then(response => response.json()).then(data => {
            setJsonQE(data);
        });
    }

    function extractHostname(raw_url) {

        var hostname;

        if (raw_url.indexOf("//") > -1) { // remove protocol
            hostname = raw_url.split('/')[2];
        } else {
            hostname = raw_url.split('/')[0];
        }
        hostname = hostname.split(':')[0]; // find & remove port number
        hostname = hostname.split('?')[0]; // find & remove "?"

        return hostname;
    }

    const getPoDS = (podval) => {
        if (podval === "Papers") {
            values.current.datasets = false;
            setpodsText("Papers");
            setDatasets(false);
        }
        else {

            values.current.datasets = true;
            setpodsText("DataSets");
            setDatasets(true);
        }
    }


    const date_formatter = (date) => {
        console.log("HERE GOES THE DATE");
        console.log(date);
        if (date == null) {
            return "inf"
        }
        else {
            let day = date.getDate();
            let month = (date.getMonth() + 1) + "-";
            let year = date.getFullYear() + "-";

            return year + month + day;
        }

    }

    function SanitizeSearch(searchval) {
        searchval.replaceAll("/", " ");
        return searchval;
    }


    const create_url = (searchq, vals) => {
        let url = "search/";
        url += SanitizeSearch(searchq).split(" ").join("+");
        url += "/";
        url += date_formatter(vals.range_from);
        url += "/";
        url += date_formatter(vals.range_to);
        url += "/";
        url += vals.algorithm.split(" ").join("_");
        url += "/";
        url += vals.searchtype.split(" ").join("_");
        url += "/";
        url += vals.datasets + "";
        url += "/";
        url += vals.pagenum + "";
        url += "/";

        return url

    }
    function TextEntered(searchval) {

        setSearch(searchval);
    }

    function getOptions(type, optval) {
        if (type === "algorithms") {
            values.current.algorithm = optval;
        }
        else if (type === "searchtype") {
            values.current.searchtype = optval;
        }
        else if (type === "author") {
            values.current.author_text = optval;
        }
        else if (type === "date_from") {
            values.current.range_from = optval;
        }
        else if (type === "date_to") {
            values.current.range_to = optval;
        }

    }



    return (
        <ThemeProvider theme={theme}>

            <div className='ResultsPage'>
                <div className='searchBar'>
                    <Box
                        sx={{
                            width: '100%',
                            height: "5em",
                            backgroundColor: '#f5f5f5'
                        }}>
                        <div style={{
                            display: 'flex',
                            flexDirection: 'row',
                            justifyContent: 'center'
                        }}>
                            <div style={{
                                marginTop: '-0.8em',
                                marginRight: '2em'
                            }}>
                                <a href="http://34.145.46.81:3000/">
                                    <img src={research_logo_side} height="100em" width="250em" />
                                </a>
                            </div>
                            <div className='Options' style={{
                                marginRight: '3em',
                                marginTop: '1.5em'
                            }}>
                                <SwipeableTemporaryDrawer hysteresis="0.52" parentCallback={getOptions} datasets={datasets} />
                            </div>
                            <div className='SearchField' style={{
                                width: '30%',
                                marginTop: '1.5em',
                                marginLeft: '1em'
                            }}>
                                {badquery ? <SearchField
                                    initialvalue={query}
                                    style={{ maxWidth: '80%' }}
                                    parentCallback={TextEntered}
                                    error={true}
                                    text={"Bad Query Was Received"}
                                />
                                    : emptyresults ? <SearchField
                                        initialvalue={query}
                                        style={{ maxWidth: '80%' }}
                                        parentCallback={TextEntered}
                                        error={true}
                                        text={"No Results were shown"}
                                    />
                                        : longquery ? <SearchField
                                            initialvalue={query}
                                            style = {{maxWidth : '80%'}}
                                            parentCallback = {TextEntered}
                                            error={true}
                                            text={"Query too long, 16 characters or less please"}
                                        />
                                            : <SearchField
                                                initialvalue={query_spaced}
                                                style={{ maxWidth: '80%' }}
                                                parentCallback={TextEntered}
                                                error={false}
                                                text={"Query"}
                                            />
                                }
                            </div>
                            <div className='SearchButton' style={{
                                marginTop: '1.5em',
                                marginLeft: '1em'
                            }}>
                                <ButtonGroup variant="contained" aria-label="outlined primary button group">
                                    <Button onClick={routeChange} variant="contained" style={{ display: 'flex', justifyContent: 'center' }}>
                                        Search
                                    </Button>
                                    <QEButton parentCallback={QueryExpansion} />
                                </ButtonGroup>
                            </div>
                            <div style={{
                                marginTop: "1em",
                                marginLeft: "1em"
                            }}>
                                <PaperOrDS parentCallback={getPoDS} dv={pods_text} />
                            </div>
                        </div> 
                    </Box>
                    <div style={{
                        display: 'flex',
                        justifyContent: 'center'
                    }}>
                        {json_query_expansion.QEResults.map(curr_elem => {
                            return <Box>{curr_elem}</Box>;
                        })}
                    </div>
                    {/* <p>moneybag yo</p> */}
                    <div className='results' style={{
                        marginLeft: '10em',
                        marginRight: '10em'
                    }}>

                        {json_results.Results.map(curr_elem => {

                            let std_date = standardize_dates(curr_elem.date);

                            return <Box padding={0.2}>
                                <p>
                                    <a href={curr_elem.url}><font size="5">{curr_elem.title}</font></a><br />
                                    <font color="#595F6A" size="2">{fix_url(curr_elem.url)} {std_date} {authorlist(curr_elem.authors)}</font><br />
                                    <font color="#595F6A">ㅤ{abstractgenerator(curr_elem.abstract)}</font><br />
                                </p></Box>;
                        })}
                    </div>
                    <div style={{
                        marginBottom: ".5em",
                        display: "flex",
                        justifyContent: "center"
                    }}>
                        <PageButton pagenum={pagenum} disableback={gobackbuttondisabled} show={showPageButton.current} sexyProp={(n) => {
                            // setPageNum(n);
                            values.current.pagenum = n;
                            routeChange();
                        }} />
                    </div>
                </div>
            </div>
        </ThemeProvider>
    )
}

