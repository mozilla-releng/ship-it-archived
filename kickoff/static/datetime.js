function convertMinutesToUtcString(totalMinutes) {
    var hours = Math.floor(totalMinutes / 60);
    var minutes = totalMinutes % 60;
    return pad(hours) + ':' + pad(minutes) + ' UTC';
}

function convertUtcStringToNumberOfMinutes(utcString) {
    var stringWithoutUtc = utcString.replace(/UTC/g, '').trim();
    var time = stringWithoutUtc.split(':');
    var hours = Number(time[0]);
    var minutes = Number(time[1]);
    return hours * 60 + minutes;
}

function convertUtcStringToNumberOfMilliseconds(string) {
    return convertUtcStringToNumberOfMinutes(string) * 60 * 1000;
}

function pad(numberToPad, width, characterToPadWith) {
    width = width || 2;
    characterToPadWith = characterToPadWith || '0';
    numberToPad = numberToPad + '';
    return numberToPad.length >= width ?
        numberToPad :
        new Array(width - numberToPad.length + 1).join(characterToPadWith) + numberToPad;
}
