output "public_ip" {
  value = aws_eip.pastebin.public_ip
}

output "public_dns" {
  value = aws_instance.pastebin.public_dns
}

output "ssh_command" {
  value = "ssh -i ~/.ssh/pastebin ubuntu@${aws_eip.pastebin.public_ip}"
}
