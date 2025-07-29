"""
Command line interface for photoframe.
"""

import os
import sys
from pathlib import Path
from typing import Optional

import click

from .core.processor import ImageProcessor
from .core.utils import get_output_path, validate_image_format
from .templates.date import DateTemplate
from .templates.baby import BabyTemplate
from .templates.camera import CameraTemplate


def get_template(template_name: str, **kwargs):
    """
    根据模板名称获取模板实例。
    
    Args:
        template_name: 模板名称
        **kwargs: 传递给模板的参数
        
    Returns:
        BaseTemplate: 模板实例
        
    Raises:
        ValueError: 如果模板名称不支持
    """
    template_classes = {
        'date': DateTemplate,
        'baby': BabyTemplate,
        'camera': CameraTemplate,
    }
    
    template_class = template_classes.get(template_name)
    if not template_class:
        available_templates = ', '.join(template_classes.keys())
        raise ValueError(f"不支持的模板: {template_name}。可用模板: {available_templates}")
    
    return template_class(**kwargs)


@click.group()
def main():
    """为照片添加水印的CLI工具"""
    pass


@main.command()
@click.argument('input_file', type=click.Path(exists=True, readable=True))
@click.option('--template', '-t', default='date',
              type=click.Choice(['date', 'baby', 'camera']),
              help='水印模板类型 (默认: date)')
@click.option('--output', '-o', type=click.Path(),
              help='输出文件路径 (默认: 自动生成)')
@click.option('--position', default='bottom-right',
              type=click.Choice(['bottom-right', 'bottom-left', 'bottom-center']),
              help='水印位置 (默认: bottom-right)')
@click.option('--opacity', default=0.8, type=click.FloatRange(0.0, 1.0),
              help='水印透明度 (0.0-1.0, 默认: 0.8)')
@click.option('--font-size', default=1.0, type=click.FloatRange(0.1, 5.0),
              help='字体大小倍数 (默认: 1.0)')
@click.option('--color', default='white',
              help='文本颜色 (默认: white)')
@click.option('--margin', default=20, type=click.IntRange(10, 200),
              help='固定边距像素 (10-200, 默认: 40)')
@click.option('--baby-birth-date', type=click.DateTime(formats=['%Y-%m-%d']),
              help='宝宝出生日期 (格式: YYYY-MM-DD, baby模板需要)')
@click.option('--custom-text',
              help='自定义水印文本')
@click.option('--dry-run', is_flag=True,
              help='预览模式，不保存文件')
@click.option('--verbose', '-v', is_flag=True,
              help='显示详细信息')
def add(input_file: str, template: str, output: Optional[str], position: str,
        opacity: float, font_size: float, color: str, margin: int, baby_birth_date,
        custom_text: Optional[str], dry_run: bool, verbose: bool):
    """
    为照片添加水印的CLI工具。
    
    INPUT_FILE: 输入图像文件路径
    
    示例:
    
    \b
    # 基础日期水印
    watermarker photo.jpg --template date
    
    \b
    # 宝宝照片带年龄
    watermarker baby.jpg --template baby --baby-birth-date 2024-01-15
    
    \b
    # 相机参数水印
    watermarker photo.jpg --template camera --position bottom-center
    """
    try:
        # 验证输入文件
        if not validate_image_format(input_file):
            click.echo(f"错误: 不支持的图像格式: {Path(input_file).suffix}", err=True)
            sys.exit(1)
        
        if verbose:
            click.echo(f"处理图像: {input_file}")
            click.echo(f"使用模板: {template}")
        
        # 创建图像处理器
        processor = ImageProcessor(input_file)
        
        if verbose:
            image_info = processor.get_image_info()
            click.echo(f"图像信息: {image_info['size'][0]}x{image_info['size'][1]}, "
                      f"方向: {image_info['orientation']}")
        
        # 准备模板参数
        template_kwargs = {
            'position': position,
            'opacity': opacity,
            'font_size': font_size,
            'color': color,
            'margin': margin,
        }
        
        # 准备渲染参数
        render_kwargs = {}
        if custom_text:
            render_kwargs['custom_text'] = custom_text
        if baby_birth_date:
            render_kwargs['birth_date'] = baby_birth_date
        
        # 特殊验证：baby模板需要出生日期
        if template == 'baby' and not baby_birth_date and not custom_text:
            click.echo("错误: baby模板需要指定 --baby-birth-date 或 --custom-text", err=True)
            sys.exit(1)
        
        # 创建模板
        try:
            template_instance = get_template(template, **template_kwargs)
        except ValueError as e:
            click.echo(f"错误: {e}", err=True)
            sys.exit(1)
        
        # 应用水印
        try:
            watermarked_image = processor.apply_watermark(template_instance, **render_kwargs)
        except ValueError as e:
            click.echo(f"错误: {e}", err=True)
            sys.exit(1)
        except Exception as e:
            click.echo(f"处理图像时出错: {e}", err=True)
            if verbose:
                import traceback
                traceback.print_exc()
            sys.exit(1)
        
        if dry_run:
            click.echo("预览模式 - 未保存文件")
            if verbose:
                click.echo("水印已成功应用到图像")
        else:
            # 确定输出路径
            output_path = get_output_path(input_file, output)
            
            # 保存图像
            try:
                processor.save_lossless(output_path, watermarked_image)
                click.echo(f"水印已添加，保存到: {output_path}")
            except Exception as e:
                click.echo(f"保存文件时出错: {e}", err=True)
                if verbose:
                    import traceback
                    traceback.print_exc()
                sys.exit(1)
        
        if verbose:
            click.echo("处理完成")
            
    except KeyboardInterrupt:
        click.echo("\n操作已取消", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"意外错误: {e}", err=True)
        if verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


@main.command()
@click.argument('input_file', type=click.Path(exists=True, readable=True))
def info(input_file: str):
    """显示图像文件的EXIF信息"""
    try:
        if not validate_image_format(input_file):
            click.echo(f"错误: 不支持的图像格式: {Path(input_file).suffix}", err=True)
            return
        
        processor = ImageProcessor(input_file)
        image_info = processor.get_image_info()
        exif_reader = processor.exif_reader
        
        click.echo(f"文件路径: {input_file}")
        click.echo(f"图像尺寸: {image_info['size'][0]}x{image_info['size'][1]}")
        click.echo(f"图像模式: {image_info['mode']}")
        click.echo(f"图像格式: {image_info['format']}")
        click.echo(f"图像方向: {image_info['orientation']}")
        
        # 显示拍摄日期
        photo_datetime = exif_reader.get_datetime()
        if photo_datetime:
            click.echo(f"拍摄日期: {photo_datetime.strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            click.echo("拍摄日期: 无")
        
        # 显示相机信息
        camera_info = exif_reader.get_camera_info()
        if camera_info['make'] or camera_info['model']:
            camera_str = f"{camera_info['make'] or ''} {camera_info['model'] or ''}".strip()
            click.echo(f"相机: {camera_str}")
        else:
            click.echo("相机: 无")
        
        # 显示镜头信息
        lens_info = exif_reader.get_lens_info()
        if lens_info['lens_model'] or lens_info['focal_length']:
            lens_str = f"{lens_info['lens_model'] or ''} {lens_info['focal_length'] or ''}".strip()
            click.echo(f"镜头: {lens_str}")
        
        # 显示拍摄设置
        settings = exif_reader.get_settings()
        settings_parts = []
        if settings['aperture']:
            settings_parts.append(settings['aperture'])
        if settings['shutter_speed']:
            settings_parts.append(settings['shutter_speed'])
        if settings['iso']:
            settings_parts.append(settings['iso'])
        
        if settings_parts:
            click.echo(f"拍摄设置: {' '.join(settings_parts)}")
        
    except Exception as e:
        click.echo(f"读取文件信息时出错: {e}", err=True)


if __name__ == '__main__':
    main()