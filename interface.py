from sys import argv, exit
from json import loads, dumps
from valexa.electron_interface.boot_validation import valexa_validate
from valexa.electron_interface.ouput import output
from valexa.electron_interface.params_export import get_params
from valexa.electron_interface.generateReport import generate, createTexZip, createPdf
from warnings import filterwarnings
import os



def main(arguments):

    if len(arguments) > 1:
        if arguments[1] == "validate":
            valexa_validate()

        if arguments[1] == "profile":
            output(**loads(arguments[2]))

        if arguments[1] == "test":
            dumps('READY')
            while(True):
                in_stream_data = input()
                if in_stream_data == '"EXIT"':
                    print("EXIT")
                    exit(0)

                parsed_stream_data = loads(in_stream_data)
                output(**parsed_stream_data)

        if arguments[1] == "get_params":
            get_params()

        if arguments[1] == "processProfilesReport":
            while(True):  # récupération du "data" de l'objet envoyé
                in_stream_data = input()

                if in_stream_data == '"EXIT"':
                    print("EXIT")
                    exit(0)
                parsed_stream_data = loads(in_stream_data)  ## dict: profiles + typeReport

                for f in os.listdir('filesTex/profiles'):  #vide dossier profiles
                    os.remove("filesTex/profiles/" + f)
                open('filesTex/ListParagraphsProfile.tex', 'w').close()  # vide file ListParagraphsProfile.tex

                for profile in parsed_stream_data['profiles']:
                    generate(**profile)

                if "tex" in parsed_stream_data['typeReport']:
                    createTexZip()
                if "pdf" in parsed_stream_data['typeReport']:
                    createPdf()

                print(dumps({"type": "END"}))

    print("EXIT")
    exit(0)


if __name__ == "__main__":
    filterwarnings("ignore")
    main(argv)
