import * as React from 'react';
import Checkbox from '@mui/material/Checkbox';
import TextField from '@mui/material/TextField';
import Autocomplete from '@mui/material/Autocomplete';
import CheckBoxOutlineBlankIcon from '@mui/icons-material/CheckBoxOutlineBlank';
import CheckBoxIcon from '@mui/icons-material/CheckBox';

const icon = <CheckBoxOutlineBlankIcon fontSize="small" />;
const checkedIcon = <CheckBoxIcon fontSize="small" />;

export default function Options(){

    return (
        <Autocomplete
        multiple
        id="checkboxes-tags-demo"
        options={top100Films}
        disableCloseOnSelect
        getOptionLabel={(option) => option.choice}
        renderOption={(props, option, { selected }) => (
            <li {...props}>
            <Checkbox
                icon={icon}
                checkedIcon={checkedIcon}
                style={{ marginRight: 8 }}
                checked={selected}
            />
            {option.choice}
            </li>
        )}
        style={{ width: 500 }}
        renderInput={(params) => (
            <TextField {...params} label="Checkboxes" placeholder="Favorites" />
        )}
        />
  );
}
const top100Films = [
  { choice: 'Research Papers'},
  { choice: 'Data Sets'}
];