import sys

def usage(file_path):
    print('Segurança de Software - Instituto Superior Técnico / Universidade Lisboa')
    print('Software Vulnerabilities Static Analysis tool: given a program, the tool reveals potential vulnerabiltiesx.\n')
    print('')
    print('Usage:')
    print('  %s <file_path> ' % file_path)
    sys.exit()


def analyse(file_path):
    print("Analysing")
    print(file_path)

if __name__ == '__main__':
    if len(sys.argv) == 2:
        analyse(sys.argv[1])
    else:
        usage(sys.argv[0])    
