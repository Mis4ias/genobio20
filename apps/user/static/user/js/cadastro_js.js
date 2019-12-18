// Comunicação com web service django para preencher as cidades
function select_cidades_por_estado(nome_cidade) {
    var id_estado = $("#state option:selected").val();

    if (id_estado != ""){
        $.getJSON( window.location.href + "select/cities", {'id_estado' : id_estado}, function(data){
            var obj = JSON.parse(JSON.stringify(data));
            add_options_cidades(obj, nome_cidade);
        });
    }
}

function add_options_cidades(obj_json, nome_cidade){
    //Removendo todos os options do select
    $('#city').find('option').remove();
    
    //Selecionando o select das cidades
    var select = document.getElementById('city'); 

    //Adicionando o option "Selecione sua cidade"
    var option = document.createElement("OPTION"); 
    option.value = "";
    option.text = "Selecione sua cidade";
    select.add(option);

    var i = 0;
    
    // Populando o select com os options contendo as cidades
    while( obj_json[i] != null )
    { 
        option = document.createElement("OPTION");
        option.value = obj_json[i].id;
        option.text  = obj_json[i].Nome;

        // Verificando se essa cidade é a cidade que veio do zipcode
        if ( nome_cidade != "" && ( obj_json[i].Nome == nome_cidade || obj_json[i].id == nome_cidade) ) { 
            option.selected = true;
        }

        select.add(option);
        i++;
    }
}

//////////////////////////////////////////////////////////////////////////////////////
    
function selected_country_brazil()
{
    document.getElementById("zipcode").disabled = false;
    document.getElementById("state").disabled = false;
    document.getElementById("city").disabled = false;
    document.getElementById("adress").disabled = false;
}

function selected_country_other()
{
    document.getElementById("zipcode").disabled = false;
    document.getElementById("state").disabled = true;
    document.getElementById("city").disabled = true;
    document.getElementById("adress").disabled = false;
    document.getElementById("state").value = "";
    document.getElementById("city").value = "";
}

function not_selected_country()
{
    document.getElementById("zipcode").disabled = true;
    document.getElementById("state").disabled = true;
    document.getElementById("city").disabled = true;
    document.getElementById("adress").disabled = true;
    document.getElementById("zipcode").value = "";
    document.getElementById("state").value = "";
    document.getElementById("city").value = "";
    document.getElementById("adress").value = "";
}

function desabilit_all()
{
    document.getElementById("zipcode").disabled = true;
    document.getElementById("state").disabled = true;
    document.getElementById("city").disabled = true;
    document.getElementById("adress").disabled = true;
}

function selected_country() 
{
    var country = $("#country option:selected");
    
    if ( country.text() == "Brazil" ){
        selected_country_brazil();
    }
    else if( country.val() == "" ){
        not_selected_country();
    }
    else{
        selected_country_other();
    }
}

//////////////////////////////////////////////////////////////////////////////////////////
      
// Limpa os valores do formulário de zipcode.
function limpa_formulário_zipcode(){ 
    $("#adress").val("");
}

function pesquisar_zipcode() 
{
    var zipcode = $('#zipcode').val().replace(/\D/g, '');
    var country = $("#country option:selected").text();

    //Verifica se campo zipcode possui valor informado.
    if (zipcode != "") 
    {
        //Expressão regular para validar o CEP.
        var validazipcode = /^[0-9]{8}$/;

        //Valida o formato do CEP.
        if( validazipcode.test(zipcode) && country == "Brazil" ){

            //Preenche os campos com "..." enquanto consulta webservice.
            var val_adress = $("#adress").val();
            $("#adress").val("Searching CEP...");
            desabilit_all();

            //Consulta o webservice viazipcode.com.br/
            $.getJSON("https://viacep.com.br/ws/"+ zipcode +"/json/?callback=?", function(dados) {

                if (!("erro" in dados)){
                    //Atualiza os campos com os valores da consulta.
                    if ( val_adress == "" ){
                        $("#adress").val(dados.bairro+" - "+dados.logradouro);
                    }else{
                        $("#adress").val(val_adress);
                    }
                    // Selecionando o estado a partir do zipcode
                    document.getElementById("state").value = $("#state").find("#"+dados.uf).val();

                    // Selecionando as cidades pertencentes aquele estado
                    select_cidades_por_estado( dados.localidade ); 
                }
                else{
                    //CEP pesquisado não foi encontrado.
                    if ($("#adress").val() == "Searching CEP...") {                        
                        $("#adress").val( val_adress );
                    }
                    alert("CEP não encontrado.");
                }

                selected_country();
            });
        }
        // CEP pesquisado não foi encontrado.
        else if (country == "Brazil"){                
            alert("Codigo postal inválido");
        }
    }
}
