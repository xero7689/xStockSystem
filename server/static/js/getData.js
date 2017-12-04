var getData = (function () {

    /* Get rank_data from self API ?!
     */
    var get_rank_list = function() {
        var req = new XMLHttpRequest();
        req.open('GET', 'http://127.0.0.1:5000/mysql', false);
        req.send( null );
        response = req.responseText;
        var jsonResponse = JSON.parse(response);
        return jsonResponse;
    };

    return {
        get_rank_list: get_rank_list
    }

})();

