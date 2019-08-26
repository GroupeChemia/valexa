export function fixedDecimals(n, precision) {
    var match = RegExp("(\\d+\\.\\d{1,"+precision+"})(\\d)?").exec(n);
    if(match===null||match[2]===undefined) {
        return Number(n).toFixed(precision);
    } else if(match[2]>=5) {
        return (Number(match[1])+Math.pow(10,-precision)).toFixed(precision);
    } else {
        return match[1];
    }
}