from time import sleep
from .core import (
    get_title, get_desc, 
    download_video, download_audio,
)    


menu = {
    1: 'Baixar Vídeo',
    2: 'Baixar Áudio',
    3: 'Sair'
}

resol = {
    1: '360p',
    2: '720p',
    3: '1080p',
    4: 'HQ',
}

def main():
    while True:
        while True:

            url = input('\nInforme o endereço web do vídeo que deseja baixar: ').strip()
            if not url:
                print('\nInforme um endereço web válido!')
                sleep(1)
            elif get_title(url) is None:
                print('\nEndereço inválido, tente novamente!')
                sleep(1)
            else:
                print(f'\nTítulo: {get_title(url)}')
                # print(f'\nDuração: {get_length(url)}')
                print(f'\nDescrição: {get_desc(url)}')
                break

        print('\n')
        for k, v in menu.items():
            print(f"{k} - {v}")

        while True:
            try:
                opt = int(input('\nSelecione uma opção: '))
            except ValueError:
                print('Digite um número válido.')
                sleep(1)
            else:
                if opt > len(menu) or opt <= 0:
                    print('Opção inválida!')
                    sleep(1)
                else:
                    break

        if opt == 1:
            print('\n')
            for k, v in resol.items():
                print(f'{k} - {v}')

            while True:
                try:
                    res = int(input('\nSelecione uma resolução: '))
                except ValueError:
                    print('Digite um número válido.')
                    sleep(1)
                else:
                    if res > len(resol) or res <= 0:
                        print('Opção inválida!')
                        sleep(1)
                    else:
                        break

            if res == 1:
                download_video(url, res)
                print('\nVídeo baixado com sucesso!!!')
                sleep(1)
            elif res == 2:
                download_video(url, res)
                print('\nVídeo baixado com sucesso!!!')
                sleep(1)
            elif res == 3:
                download_video(url, res)
                print('\nVídeo baixado com sucesso!!!')
                sleep(1)
            elif res == 4:
                download_video(url, res)
                print('\nVídeo baixado com sucesso!!!')
                sleep(1)

        if opt == 2:
            download_audio(url)
            print('\nÁudio baixado com sucesso!')
            sleep(1)

        if opt == 3:
            print('\nPrograma finalizado!')
            sleep(1)
            break

        print('\nDeseja baixar outro video/audio ?')
        try:
            answer = input('\n1 - SIM / 2 - NAO:   ' ).strip()[0]
        except ValueError:
            print('\nInforme um valor válido!')
            sleep(1)
        else:
            if int(answer) < 1 or int(answer) > 2:
                print('\nResposta incorreta.')
                sleep(1)

        if answer == '2':
            print('\nPrograma finalizado!')
            sleep(1)
            break


if __name__ == '__main__':
    main()
