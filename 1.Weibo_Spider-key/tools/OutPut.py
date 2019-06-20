import xlsxwriter
import json

def generate_xlsx(data_list, filename):
    """
    输入dict构成的list，生成xlsl数据
    :return:
    """
    filename = filename.replace(".txt", "")
    filename = filename.replace(".json", "")
    filename += ".xlsx"
    workbook = xlsxwriter.Workbook(filename)
    worksheet = workbook.add_worksheet()

    worksheet.write('A1', 'text')
    worksheet.write('B1', 'datetime')
    worksheet.write('C1', 'location')

    for r, data in enumerate(data_list):
        worksheet.write_string(r+1, 0, str(data["wb_content"]))
        worksheet.write_string(r+1, 1, str(data["wb_createtime"]))
        if data["wb_place"] != []:
            worksheet.write_string(r+1, 2, str(data["wb_place"][0]))
        else:
            worksheet.write_string(r + 1, 2, "")
    workbook.close()
    print("xlsx文件生成成功！")


if __name__ == '__main__':
    data = json.load(open("../data_store/山竹_2018.9.14.0_2018.9.19.0"))
    generate_xlsx(data, "../data_store/山竹_2018.9.14.0_2018.9.19.0")
    print("xlsx生成成功！")

