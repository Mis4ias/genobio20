/*!
 * @brief Retira todos os campos que mostram os dados do usuário
 * e coloca os inputs para o usuário alterar seus dados.
 */
function alter_data() {
    var x = document.getElementsByClassName('datauser');
    var y = document.getElementsByClassName('datap');

    for(var i=0; i<x.length; i++){
        x[i].style ='display:block;';
        y[i].style ='display:none;';
    }

}

function sendFile(){
    document.getElementById('inputReceipt').click();
}

/*!
 * @brief Função executada quando o tamanho da tela é alterado 
 * para verificar e decidir de que forma o menu de opções será
 * paresentado, normal ou comocollapase.
 */
window.onresize = function() {
    if ( window.innerWidth < 767.98 ){
        if ( ! $("#signed-tab").hasClass("collapse") )
        {
            $("#signed-tab").addClass("collapse");
        }
    }
    else if ( $("#signed-tab").hasClass("collapse") )
    {
        $("#signed-tab").removeClass("collapse");
        $("#signed-tab").css("height", "");
    }
}  

/*!
 * @brief Função executada quando a página é carregada. Ela 
 * verifica se é uma tela de celular e mostra o menu de opções
 * como collapase.
*/
window.onload = function(){
    if( window.innerWidth < 767.98)
    {   
        $("#signed-tab").addClass("collapse");
    }
} 